from typing import Dict, Tuple, Any
from game_state import GameState, Tile, TurnState
from utils.logger import logger

def move_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get current turn's state
    current_turn = game_state.current_turn
    turn_state = game_state.turns[current_turn]
    
    # Check if moves exist in input_moves for this hex
    if hex_pos not in turn_state.input_moves:
        return game_state
    
    world = dict(game_state.world)
    moves = {
        1: turn_state.input_moves.get(hex_pos, {}).get(1, []),
        2: turn_state.input_moves.get(hex_pos, {}).get(2, [])
    }
    
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
    
    # Create new turn state with updated world
    move_record = {
        'source': hex_pos,
        'destination': dest_pos,
        'units': units_to_move,
        'player_id': player_id
    }
    
    new_turn_state = TurnState(
        turn_number=turn_state.turn_number,
        world=world,
        player_one=turn_state.player_one,
        player_two=turn_state.player_two,
        input_moves=turn_state.input_moves,
        move_actions=[*turn_state.move_actions, move_record],  # Add new move to existing moves
        spawn_actions=turn_state.spawn_actions,
        combat_actions=turn_state.combat_actions
    )
    
    # Update turns dictionary
    turns = dict(game_state.turns)
    turns[current_turn] = new_turn_state
    
    return GameState.from_state(game_state, world=world, turns=turns) 