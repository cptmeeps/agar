from typing import Dict, Tuple, Any
from game_state import GameState, Tile, TurnState, PlayerState
from utils.logger import logger

def move_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get current turn's state
    current_turn = game_state.current_turn
    turn_state = game_state.turns[current_turn]
    # print(f"DEBUG - move_action - Current turn: {current_turn}")
    
    # Check if moves exist in input_moves for this hex
    if hex_pos not in turn_state.input_moves:
        return game_state
    
    world = dict(game_state.world)
    moves = {
        1: turn_state.input_moves.get(hex_pos, {}).get(1, []),
        2: turn_state.input_moves.get(hex_pos, {}).get(2, [])
    }
    
    move_records = []  # Initialize list of move records
    
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
            
            # Create move record for each move
            move_record = {
                'source': hex_pos,
                'destination': dest_pos,
                'units': units_to_move,
                'player_id': player_id
            }
            move_records.append(move_record)
    
    # Update turn state
    turns = dict(game_state.turns)
    
    # Update player states using from_state
    new_player_one = PlayerState.from_state(turn_state.player_one)
    new_player_two = PlayerState.from_state(turn_state.player_two)

    new_turn_state = TurnState(
        turn_number=turn_state.turn_number,
        world=world,
        player_one=new_player_one,
        player_two=new_player_two,
        input_moves=turn_state.input_moves,
        move_actions=[*turn_state.move_actions, *move_records],
        spawn_actions=turn_state.spawn_actions,
        combat_actions=turn_state.combat_actions
    )
        
    turns[current_turn] = new_turn_state
    
    new_game_state = (GameState.builder(game_state)
                      .with_world(world)
                      .with_turns(turns)
                      .build())
    
    return new_game_state

def main():
    # Create a test configuration
    test_config = {
        'board_size': 5,
        'max_turns': 10,
        'num_players': 2,
        'player_one_config': {
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        },
        'player_two_config': {
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        }
    }

    # Create initial game state
    game_state = GameState.from_config(test_config)
    
    # Create some test moves
    test_moves = {
        (0, 2): {  # Starting position for player 1
            1: [{'destination': (1, 2), 'units': 2}],
            2: []
        },
        (4, 2): {  # Starting position for player 2
            1: [],
            2: [{'destination': (3, 2), 'units': 2}]
        }
    }
    
    # Update the turn state with test moves
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]
    
    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=game_state.world,
        player_one=current_turn_state.player_one,
        player_two=current_turn_state.player_two,
        input_moves=test_moves
    )
    
    turns = dict(game_state.turns)
    turns[current_turn] = new_turn_state
    game_state = GameState.builder(game_state).with_turns(turns).build()

    print("\n" + "="*80)
    print("Testing move_action")
    print("Expected: Units should move from source positions to destinations")
    print("="*80)

    # Print initial state
    print("\nInitial board state:")
    for pos, tile in game_state.world.items():
        if tile.units:
            print(f"Position {pos}: {len(tile.units)} units (Player IDs: {[unit.player_id for unit in tile.units]})")

    # Test moves from both starting positions
    print("\nProcessing moves...")
    
    # Process moves from (0,2)
    print("\nProcessing moves from (0,2):")
    new_state = move_action(game_state, (0, 2))
    for pos, tile in new_state.world.items():
        if tile.units:
            print(f"Position {pos}: {len(tile.units)} units (Player IDs: {[unit.player_id for unit in tile.units]})")
    
    # Process moves from (4,2)
    print("\nProcessing moves from (4,2):")
    final_state = move_action(new_state, (4, 2))
    for pos, tile in final_state.world.items():
        if tile.units:
            print(f"Position {pos}: {len(tile.units)} units (Player IDs: {[unit.player_id for unit in tile.units]})")

    # Print move records
    print("\nMove records:")
    final_turn_state = final_state.turns[final_state.current_turn]
    for move in final_turn_state.move_actions:
        print(f"Player {move['player_id']} moved {move['units']} units from {move['source']} to {move['destination']}")

if __name__ == "__main__":
    main() 