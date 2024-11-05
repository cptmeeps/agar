from typing import Dict, Tuple, Any
from game_state import GameState, Tile
from utils.logger import logger

def move_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get current turn's moves from turns dictionary
    current_turn = game_state.current_turn
    turn_data = game_state.turns.get(current_turn, {})
    turn_input = turn_data.get('turn_input', {})

    if ('moves' not in turn_input or hex_pos not in turn_input['moves']):
        return game_state
    
    world = dict(game_state.world)
    moves = turn_input['moves'][hex_pos]
    
    for player_id, player_moves in moves.items():
        for move in player_moves:
            source_tile = world[hex_pos]
            dest_pos = move['destination']
            units_to_move = move['units']
            
            if dest_pos not in world or len(source_tile.units) < units_to_move:
                continue
            
            moving_units = source_tile.units[:units_to_move]
            remaining_units = source_tile.units[units_to_move:]
            
            # Update tiles
            world[hex_pos] = Tile(position=source_tile.position, units=remaining_units)
            dest_tile = world[dest_pos]
            world[dest_pos] = Tile(position=dest_tile.position, units=list(dest_tile.units) + moving_units)
            
            # Log the movement
            logger.log_movement(
                game_state,
                hex_pos,
                dest_pos,
                units_to_move,
                player_id
            )
    
    return GameState(**{**game_state.__dict__, 'world': world}) 