# Strategy game built using functional programming principles in Python.

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto

# Type definitions
class TerrainType(Enum):
    PLAINS = "plains"

class UnitType(Enum):
    WARRIOR = "warrior"

class Phase(Enum):
    MOVEMENT = auto()
    COMBAT = auto()
    SPAWN = auto()

@dataclass(frozen=True)
class Position:
    q: int  # axial coordinates
    r: int
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.q + other.q, self.r + other.r)

@dataclass(frozen=True)
class Unit:
    unit_type: UnitType
    player_id: int
    health: int
    movement_points: int

@dataclass(frozen=True)
class Tile:
    position: Position
    terrain: TerrainType
    units: List[Unit] = field(default_factory=list)

@dataclass(frozen=True)
class TurnState:
    phase: Phase

@dataclass(frozen=True)
class GameState:
    tiles: Dict[Tuple[int, int], Tile]
    turn_number: int
    turn_state: TurnState

@dataclass(frozen=True)
class MoveAction:
    unit_position: Position
    target_position: Position

@dataclass(frozen=True)
class CombatAction:
    position: Position  # Combat happens automatically at this position

@dataclass(frozen=True)
class SpawnAction:
    position: Position

# Union type for all possible actions
ActionType = Union[MoveAction, CombatAction, SpawnAction]

def create_game_state(size: int) -> GameState:
    tiles = {}
    for q in range(-size, size + 1):
        r1 = max(-size, -q - size)
        r2 = min(size, -q + size)
        for r in range(r1, r2 + 1):
            pos = Position(q, r)
            tiles[(q, r)] = Tile(pos, TerrainType.PLAINS)
    
    initial_turn_state = TurnState(phase=Phase.MOVEMENT)
    return GameState(
        tiles=tiles,
        turn_number=1,
        turn_state=initial_turn_state
    )

def advance_phase(game_state: GameState) -> GameState:
    current_phase = game_state.turn_state.phase
    
    if current_phase == Phase.MOVEMENT:
        new_phase = Phase.COMBAT
    elif current_phase == Phase.COMBAT:
        new_phase = Phase.SPAWN
    else:  # SPAWN phase
        new_phase = Phase.MOVEMENT
        # Only increment turn during phase transition
        new_turn = game_state.turn_number + 1
        return GameState(
            tiles=game_state.tiles,
            turn_number=new_turn,
            turn_state=TurnState(phase=new_phase)
        )
    
    return GameState(
        tiles=game_state.tiles,
        turn_number=game_state.turn_number,
        turn_state=TurnState(phase=new_phase)
    )

def execute_turn_action(game_state: GameState, action: ActionType, player_id: int) -> GameState:
    if isinstance(action, MoveAction):
        return _apply_move(game_state, action, player_id)
    elif isinstance(action, CombatAction):
        return _apply_combat(game_state, action)
    else:  # SpawnAction
        return process_spawn_phase(game_state)  # Spawn phase now handles both players

def apply_action(game_state: GameState, action: ActionType) -> GameState:
    if isinstance(action, MoveAction):
        return _apply_move(game_state, action)
    elif isinstance(action, CombatAction):
        return _apply_combat(game_state, action)
    else:  # SpawnAction
        return _apply_spawn(game_state, action)

# Move-related functions
def _apply_move(game_state: GameState, action: MoveAction, player_id: int) -> GameState:
    source_pos = (action.unit_position.q, action.unit_position.r)
    target_pos = (action.target_position.q, action.target_position.r)
    
    source_tile = game_state.tiles[source_pos]
    target_tile = game_state.tiles[target_pos]
    
    # Find the first unit belonging to the specified player
    unit_to_move = next(unit for unit in source_tile.units 
                       if unit.player_id == player_id)
    
    # Create new unit lists
    new_source_units = [u for u in source_tile.units if u != unit_to_move]
    new_target_units = list(target_tile.units) + [unit_to_move]
    
    # Create new tiles
    new_tiles = dict(game_state.tiles)
    new_tiles[source_pos] = Tile(source_tile.position, source_tile.terrain, new_source_units)
    new_tiles[target_pos] = Tile(target_tile.position, target_tile.terrain, new_target_units)
    
    return GameState(
        tiles=new_tiles,
        turn_number=game_state.turn_number,
        turn_state=game_state.turn_state
    )

def get_player_moves(game_state: GameState, player_id: int) -> List[MoveAction]:
    # TODO: Implement actual player input logic
    return []

# Combat-related functions
def _apply_combat(game_state: GameState, action: CombatAction) -> GameState:
    pos = (action.position.q, action.position.r)
    tile = game_state.tiles[pos]
    
    # Separate units by player
    player1_units = [u for u in tile.units if u.player_id == 1]
    player2_units = [u for u in tile.units if u.player_id == 2]
    
    # Calculate total damage for each side
    p1_damage = len(player1_units) * 3  # 3 damage per unit as per README
    p2_damage = len(player2_units) * 3
    
    # Calculate damage per unit
    p1_damage_per_unit = p2_damage / len(player1_units) if player1_units else 0
    p2_damage_per_unit = p1_damage / len(player2_units) if player2_units else 0
    
    # Apply damage and filter out dead units
    surviving_units = []
    for unit in player1_units + player2_units:
        damage = p1_damage_per_unit if unit.player_id == 2 else p2_damage_per_unit
        new_health = unit.health - damage
        if new_health > 0:
            surviving_units.append(Unit(
                unit_type=unit.unit_type,
                player_id=unit.player_id,
                health=new_health,
                movement_points=unit.movement_points
            ))
    
    # Update tile with surviving units
    new_tiles = dict(game_state.tiles)
    new_tiles[pos] = Tile(tile.position, tile.terrain, surviving_units)
    
    return GameState(
        tiles=new_tiles,
        turn_number=game_state.turn_number,
        turn_state=game_state.turn_state
    )

def process_combat_phase(game_state: GameState) -> GameState:
    new_tiles = dict(game_state.tiles)
    
    # Find all tiles with units from both players
    for pos, tile in game_state.tiles.items():
        player1_units = [u for u in tile.units if u.player_id == 1]
        player2_units = [u for u in tile.units if u.player_id == 2]
        
        if player1_units and player2_units:
            # Create and apply combat action for this position
            combat_action = CombatAction(Position(pos[0], pos[1]))
            game_state = _apply_combat(game_state, combat_action)
    
    return game_state

# Spawn-related functions
def _apply_spawn(game_state: GameState, action: SpawnAction) -> GameState:
    pos = (action.position.q, action.position.r)
    tile = game_state.tiles[pos]
    
    # Create new unit
    new_unit = Unit(
        unit_type=UnitType.WARRIOR,
        player_id=game_state.current_player,
        health=10,  # Initial health as per README
        movement_points=1
    )
    
    # Add new unit to tile
    new_units = list(tile.units) + [new_unit]
    
    # Update tile
    new_tiles = dict(game_state.tiles)
    new_tiles[pos] = Tile(tile.position, tile.terrain, new_units)
    
    return GameState(
        tiles=new_tiles,
        turn_number=game_state.turn_number,
        turn_state=game_state.turn_state
    )

def process_spawn_phase(game_state: GameState) -> GameState:
    new_tiles = dict(game_state.tiles)
    
    # Process spawns for both players
    for player_id in [1, 2]:
        # Find all valid spawn locations for current player
        for pos, tile in game_state.tiles.items():
            player_units = [u for u in tile.units if u.player_id == player_id]
            enemy_units = [u for u in tile.units if u.player_id != player_id]
            
            # If we have units and no enemy units, this is a valid spawn location
            if player_units and not enemy_units:
                # Create new unit
                new_unit = Unit(
                    unit_type=UnitType.WARRIOR,
                    player_id=player_id,
                    health=10,
                    movement_points=1
                )
                
                # Add new unit to tile
                new_units = list(tile.units) + [new_unit]
                new_tiles[pos] = Tile(tile.position, tile.terrain, new_units)
    
    return GameState(
        tiles=new_tiles,
        turn_number=game_state.turn_number,
        turn_state=game_state.turn_state
    )

def is_game_over(game_state: GameState) -> bool:
    # Check for turn limit
    if game_state.turn_number > 100:
        return True
        
    # Count units for each player
    player1_units = 0
    player2_units = 0
    
    # Check all tiles for units
    for tile in game_state.tiles.values():
        for unit in tile.units:
            if unit.player_id == 1:
                player1_units += 1
            elif unit.player_id == 2:
                player2_units += 1
    
    # Game is over if either player has no units
    return player1_units == 0 or player2_units == 0

def run_game(initial_state: GameState) -> GameState:
    current_state = initial_state
    
    while not is_game_over(current_state):
        if current_state.turn_state.phase == Phase.MOVEMENT:
            # Display game state to both players
            display_game_state(current_state)
            
            # Get moves from both players simultaneously
            player1_moves = get_player_moves(current_state, 1)
            player2_moves = get_player_moves(current_state, 2)
            
            # Apply all movement actions
            for move in player1_moves:
                current_state = execute_turn_action(current_state, move, 1)
            for move in player2_moves:
                current_state = execute_turn_action(current_state, move, 2)
            
            current_state = advance_phase(current_state)
            
        elif current_state.turn_state.phase == Phase.COMBAT:
            current_state = process_combat_phase(current_state)
            current_state = advance_phase(current_state)
            
        else:  # SPAWN phase
            current_state = process_spawn_phase(current_state)
            current_state = advance_phase(current_state)
    
    return current_state

def display_game_state(game_state: GameState) -> None:
    print("\n=== Game State ===")
    print(f"Turn Number: {game_state.turn_number}")
    print(f"Current Phase: {game_state.turn_state.phase.name}")
    print("\nTiles:")
    for pos, tile in game_state.tiles.items():
        if tile.units:  # Only show tiles with units
            print(f"\nPosition {pos}:")
            for unit in tile.units:
                print(f"  Player {unit.player_id} {unit.unit_type.value}: "
                      f"HP={unit.health}, MP={unit.movement_points}")
    print("\n================\n")

