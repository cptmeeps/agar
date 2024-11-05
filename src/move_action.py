from typing import Dict, Tuple, Any
from game_types import Tile
from game_state import GameState, create_sample_game_state

def move_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get current turn's moves from turns dictionary
    current_turn = game_state.current_turn
    turn_data = game_state.turns.get(current_turn, {})
    turn_input = turn_data.get('turn_input', {})

    # If no moves exist or this hex isn't a source of any moves, return unchanged
    if ('moves' not in turn_input or 
        hex_pos not in turn_input['moves']):
        return game_state
    
    world = dict(game_state.world)
    moves = turn_input['moves'][hex_pos]
    # print("moves at", hex_pos, ":",moves)
    
    # Process moves for each player
    for player_id, player_moves in moves.items():
        # Process each move from this player
        for move in player_moves:
            # Get current state of source tile
            source_tile = world[hex_pos]
            
            dest_pos = move['destination']
            units_to_move = move['units']
            
            # Skip if destination isn't valid
            if dest_pos not in world:
                continue
            
            # Skip if not enough units available
            if len(source_tile.units) < units_to_move:
                continue
            
            # Move units from source to destination
            # print(f"Turn {current_turn}: Moving {units_to_move} units from player {player_id} from {hex_pos} to {dest_pos}")
            moving_units = source_tile.units[:units_to_move]
            remaining_units = source_tile.units[units_to_move:]
            # print("remaining_units at", hex_pos, ":", remaining_units)
            
            # Update source tile
            world[hex_pos] = Tile(
                position=source_tile.position,
                units=remaining_units
            )
            
            # Update destination tile
            dest_tile = world[dest_pos]
            world[dest_pos] = Tile(
                position=dest_tile.position,
                units=list(dest_tile.units) + moving_units
            )
    
    return GameState(**{**game_state.__dict__, 'world': world}) 