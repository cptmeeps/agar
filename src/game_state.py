from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

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
                world=world
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