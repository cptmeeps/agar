from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from enum import Enum


@dataclass(frozen=True)
class Position:
    x: int 
    y: int
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)

@dataclass(frozen=True)
class Unit:
    player_id: int
    health: int
    movement_points: int

@dataclass(frozen=True)
class Tile:
    position: Position
    units: List[Unit] = field(default_factory=list)

@dataclass(frozen=True)
class PlayerState:
    player_config: Dict[str, Any] = field(default_factory=dict)
    turn_msg_chain: List[Dict[str, str]] = field(default_factory=list)
    turn_model_output: Dict[str, Any] = field(default_factory=lambda: {'moves': []})
    turn_input: Dict[str, Any] = field(default_factory=dict)
    turn_prompt_chain: List[Dict[str, str]] = field(default_factory=list)
    turn_prompt_config: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_state(cls, state: 'PlayerState', **updates) -> 'PlayerState':
        """Creates a new PlayerState from an existing one with optional updates."""
        state_dict = state.__dict__.copy()
        state_dict.update(updates)
        return cls(**state_dict)

@dataclass(frozen=True)
class TurnState:
    turn_number: int = 1
    world: Dict[Tuple[int, int], Tile] = field(default_factory=dict)
    player_one: PlayerState = field(default_factory=PlayerState)
    player_two: PlayerState = field(default_factory=PlayerState)
    input_moves: Dict[Tuple[int, int], Dict[int, List[Dict[str, Any]]]] = field(default_factory=dict)  # Structure: {(x,y): {player_id: [{'destination': (x,y), 'units': n}, ...]}}}
    move_actions: List[Dict[str, Any]] = field(default_factory=list)  # Structure: [{'source': (x,y), 'destination': (x,y), 'units': n, 'player_id': id}, ...]
    spawn_actions: List[Dict[str, Any]] = field(default_factory=list)  # Structure: [{'position': (x,y), 'player_id': id}, ...]
    combat_actions: List[Dict[str, Any]] = field(default_factory=list)  # Structure: [{'position': (x,y), 'player_1_casualties': n, 'player_2_casualties': n}, ...]

@dataclass(frozen=True)
class SpawnStateChange:
    world_updates: Dict[Tuple[int, int], Tile]
    turn_state_update: TurnState
    
@dataclass(frozen=True)
class CombatStateChange:
    world_updates: Dict[Tuple[int, int], Tile]
    turn_state_update: TurnState

@dataclass(frozen=True)
class GameState:
    world: Dict[Tuple[int, int], Tile]
    current_turn: int
    max_turns: int
    num_players: int
    game_status: str
    game_end_criteria: Dict[str, Any]
    player_one_config: Dict[str, Any]
    player_two_config: Dict[str, Any]
    turns: Dict[int, TurnState]

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'GameState':
        # Create a simple world based on config
        world = {}
        size = config.get('board_size', 5)
        
        for x in range(size):
            for y in range(size):
                pos = (x, y)
                units = []
                # Add player 1's unit at (0, 2) - left side
                if x == 0 and y == 2:
                    units = [
                        Unit(player_id=1, health=1, movement_points=1),
                        Unit(player_id=1, health=1, movement_points=1)
                    ]
                # Add player 2's unit at (4, 2) - right side
                elif x == size-1 and y == 2:
                    units = [
                        Unit(player_id=2, health=1, movement_points=1),
                        Unit(player_id=2, health=1, movement_points=1)
                    ]
                
                world[pos] = Tile(Position(x, y), units)
        
        # Create all TurnStates from 1 to max_turns
        max_turns = config.get('max_turns', 10)
        turns = {}
        for turn_num in range(1, max_turns + 1):
            turns[turn_num] = TurnState(
                turn_number=turn_num,
                world=world,
                player_one=PlayerState(
                    player_config=config.get('player_one_config', {}),
                    turn_prompt_config=config.get('player_one_config', {}).get('turn_prompt_config', [])
                ),
                player_two=PlayerState(
                    player_config=config.get('player_two_config', {}),
                    turn_prompt_config=config.get('player_two_config', {}).get('turn_prompt_config', [])
                )
            )

        return cls(
            world=world,
            current_turn=1,
            max_turns=max_turns,
            num_players=config.get('num_players', 2),
            game_status="in_progress",
            game_end_criteria=config.get('end_criteria', {'type': 'elimination'}),
            player_one_config=config.get('player_one_config', {}),
            player_two_config=config.get('player_two_config', {}),
            turns=turns
        )

    @classmethod
    def from_state(cls, state: 'GameState', **updates) -> 'GameState':
        # Create new state from existing one, with optional updates
        state_dict = state.__dict__.copy()
        state_dict.update(updates)
        return cls(**state_dict)

    def is_valid_state_change(self, new_state: 'GameState', phase: str | None = None) -> bool:
        # TODO: Implement validation logic for each phase
        # For now, always return True
        return True

    @classmethod
    def builder(cls, state: 'GameState') -> 'GameStateBuilder':
        """Creates a builder initialized with the current state"""
        return GameStateBuilder(state)

    def apply_spawn_change(self, change: SpawnStateChange) -> 'GameState':
        world = dict(self.world)
        world.update(change.world_updates)
        
        turns = dict(self.turns)
        turns[self.current_turn] = change.turn_state_update
        
        return GameState.from_state(self, world=world, turns=turns)

    def apply_event(self, event: 'GameEvent') -> 'GameState':
        if event.type == GameEvent.Type.SPAWN:
            return self._apply_spawn_event(event.data)
        elif event.type == GameEvent.Type.COMBAT:
            return self._apply_combat_event(event.data)
        # ... etc
        
    def _apply_spawn_event(self, data: Dict[str, Any]) -> 'GameState':
        world = dict(self.world)
        turns = dict(self.turns)
        # Apply specific spawn changes
        return GameState.from_state(self, world=world, turns=turns)

    def print_world(self):
        """Helper function to print the current world state in a grid format."""
        # Find the bounds of the world
        xs = [pos[0] for pos in self.world.keys()]
        ys = [pos[1] for pos in self.world.keys()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        print("\nWorld:")
        print("-" * 40)  
        # Print header
        print("    ", end="")
        for x in range(min_x, max_x + 1):
            print(f"|{x:^5}", end="")
        print("|")
        
        # Print separator line
        print("    " + "-" * ((max_x - min_x + 1) * 6 + 1))
        
        for y in range(min_y, max_y + 1):
            print(f"{y:2d}  ", end="")
            for x in range(min_x, max_x + 1):
                tile = self.world.get((x, y), None)
                counts = {1: 0, 2: 0}
                if tile and tile.units:
                    for unit in tile.units:
                        counts[unit.player_id] = counts.get(unit.player_id, 0) + 1
                
                p1_display = '•' if counts[1] == 0 else str(counts[1])
                p2_display = '•' if counts[2] == 0 else str(counts[2])
                print(f"|{p1_display:>2} {p2_display:<2}", end="")
            print("|")
        
        # Print separator line
        print("    " + "-" * ((max_x - min_x + 1) * 6 + 1))
        print("     " + "P1 P2 " * (max_x - min_x + 1))
        print()

class GameStateBuilder:
    def __init__(self, original_state: GameState):
        self._original = original_state
        self._changes = {}
    
    def with_world(self, world: Dict[Tuple[int, int], Tile]) -> 'GameStateBuilder':
        """Updates the world state"""
        self._changes['world'] = world
        return self
    
    def with_turns(self, turns: Dict[int, TurnState]) -> 'GameStateBuilder':
        """Updates the turns dictionary"""
        self._changes['turns'] = turns
        return self
    # TODO: Check if this is correct, I don't think there is a current_turn in the GameState class
    def with_current_turn(self, turn: int) -> 'GameStateBuilder':
        """Updates the current turn number"""
        self._changes['current_turn'] = turn
        return self
        
    def build(self) -> GameState:
        """Creates new GameState with all changes applied"""
        state_dict = self._original.__dict__.copy()
        state_dict.update(self._changes)
        return GameState(**state_dict)

class GameEvent:
    class Type(Enum):
        SPAWN = "spawn"
        COMBAT = "combat"
        MOVE = "move"
        
    def __init__(self, type: Type, data: Dict[str, Any]):
        self.type = type
        self.data = data