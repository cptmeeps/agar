from typing import Dict, Tuple, Any
from game_types import GameState, Tile

def move_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get current turn's moves from turns dictionary
    current_turn = game_state.current_turn
    turn_data = game_state.turns.get(current_turn, {})
    turn_input = turn_data.get('turn_input', {})

    # Add move information, in the format:
    # turns = {
    #     1: {
    #         'turn_input': {
    #             'moves': {
    #                 (0, 2): {  # source position
    #                     1: [  # player_id
    #                         {'destination': (1, 2), 'units': 2},
    #                         {'destination': (0, 3), 'units': 1}
    #                     ],
    #                     2: [
    #                         {'destination': (0, 1), 'units': 1}
    #                     ]
    #                 }
    #             }
    #         }
    #     }
    # }

    # If no moves exist or this hex isn't a source of any moves, return unchanged
    if ('moves' not in turn_input or 
        hex_pos not in turn_input['moves']):
        return game_state
    
    world = dict(game_state.world)
    moves = turn_input['moves'][hex_pos]
    source_tile = world[hex_pos]
    
    # Process moves for each player
    for player_id, player_moves in moves.items():
        # Process each move from this player
        for move in player_moves:
            dest_pos = move['destination']
            units_to_move = move['units']
            
            # Skip if destination isn't valid
            if dest_pos not in world:
                continue
            
            # Skip if not enough units available
            if len(source_tile.units) < units_to_move:
                continue
            
            # Move units from source to destination
            moving_units = source_tile.units[:units_to_move]
            remaining_units = source_tile.units[units_to_move:]
            
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