from typing import Dict, Tuple, Any
from game_state import GameState, Tile, PlayerState, TurnState
from utils.llm import create_message_chain, call_llm_api
from utils.prompt import generate_prompt_chain
import json
from utils.logger import logger

def create_llm_world_representation(game_state: GameState, player_id: int) -> Dict[str, Any]:
    opponent_id = 2 if player_id == 1 else 1
    
    world_representation = {
        "game_info": {
            "current_turn": game_state.current_turn,
            "max_turns": game_state.max_turns,
            "game_status": game_state.game_status
        },
        "board": {
            "controlled_territories": {
                "your_territory": [],
                "enemy_territory": []
            },
            "cells": {}
        }
    }

    # Find board dimensions
    xs = [pos[0] for pos in game_state.world.keys()]
    ys = [pos[1] for pos in game_state.world.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Initialize all cells with zero units
    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            world_representation["board"]["cells"][f"{x},{y}"] = {
                "position": {"x": x, "y": y},
                "units": {
                    "your_units": 0,
                    "enemy_units": 0
                },
                "controlled_by": None
            }

    # Update cells with actual unit counts
    for pos, tile in game_state.world.items():
        x, y = pos
        cell_key = f"{x},{y}"
        
        # Count units for each player
        your_units = sum(1 for unit in tile.units if unit.player_id == player_id)
        enemy_units = sum(1 for unit in tile.units if unit.player_id == opponent_id)
        
        # Update unit counts
        world_representation["board"]["cells"][cell_key]["units"]["your_units"] = your_units
        world_representation["board"]["cells"][cell_key]["units"]["enemy_units"] = enemy_units

        # Determine control
        if your_units > 0 and enemy_units == 0:
            world_representation["board"]["cells"][cell_key]["controlled_by"] = "you"
            world_representation["board"]["controlled_territories"]["your_territory"].append(
                {"x": x, "y": y}
            )
        elif enemy_units > 0 and your_units == 0:
            world_representation["board"]["cells"][cell_key]["controlled_by"] = "enemy"
            world_representation["board"]["controlled_territories"]["enemy_territory"].append(
                {"x": x, "y": y}
            )

    return world_representation


def get_ai_moves(game_state: GameState, player_id: int) -> Dict[str, Any]:
    # Create game state representation
    world_representation = create_llm_world_representation(game_state, player_id)
    
    # Get current player state
    current_turn_state = game_state.turns[game_state.current_turn]
    player_state = current_turn_state.player_one if player_id == 1 else current_turn_state.player_two

    # Ensure prompt_configs is properly formatted
    prompt_configs = player_state.turn_prompt_config
    if not isinstance(prompt_configs, list):
        prompt_configs = [prompt_configs]
    
    # Validate prompt configs
    for config in prompt_configs:
        if not isinstance(config, dict) or 'prompt_filepath' not in config:
            raise ValueError("Each prompt config must be a dictionary with a 'prompt_filepath' key")
        
        if 'template_params' not in config:
            config['template_params'] = {}
        config['template_params']['world_representation'] = world_representation
    
    # Generate prompt chain
    prompt_chain = generate_prompt_chain(prompt_configs)

    # Create message chain from prompt chain
    message_chain = create_message_chain(prompt_chain)
    
    # Get LLM response
    response = call_llm_api(message_chain)
    try:
        response = json.loads(response)
    except json.JSONDecodeError:
        print("Error: LLM response is not a valid JSON.")
        # Optionally handle the error further, e.g., return an empty dictionary or raise an exception
        return {}
    logger.log_action(
        "ai_move_generation",
        game_state,
        details={"player_id": player_id, "moves": response.get("moves", [])}
    )
    return response

def get_input_action(game_state: GameState, cell_pos: Tuple[int, int]) -> GameState:
    # Get current turn state
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]

    # Get moves from both AIs
    player_one_moves = get_ai_moves(game_state, 1)
    player_two_moves = get_ai_moves(game_state, 2)
    
    # Initialize all_moves dictionary
    all_moves = {}
    
    # Track remaining units at each source position for each player
    remaining_units = {}

    # First pass: Initialize remaining units count
    for source, player_moves in [
        (1, player_one_moves.get('moves', [])), 
        (2, player_two_moves.get('moves', []))
    ]:
        for move in player_moves:
            source_pos = tuple(move['source'])
            if source_pos not in game_state.world:
                continue
                
            if source_pos not in remaining_units:
                remaining_units[source_pos] = {}
                source_tile = game_state.world[source_pos]
                for player_id in [1, 2]:
                    remaining_units[source_pos][player_id] = sum(
                        1 for unit in source_tile.units if unit.player_id == player_id
                    )

    # Process and validate moves for each player
    for source, player_moves in [
        (1, player_one_moves.get('moves', [])), 
        (2, player_two_moves.get('moves', []))
    ]:
        for move in player_moves:
            source_pos = tuple(move['source'])
            
            if source_pos not in game_state.world:
                continue
                
            if source_pos not in all_moves:
                all_moves[source_pos] = {1: [], 2: []}
            
            available_units = remaining_units[source_pos][source]
            
            if available_units <= 0:
                continue
                
            units_to_move = min(move['units'], available_units)
            remaining_units[source_pos][source] -= units_to_move
            
            all_moves[source_pos][source].append({
                'destination': tuple(move['destination']),
                'units': units_to_move
            })

    # Create new player states using from_state
    new_player_one = PlayerState.from_state(
        current_turn_state.player_one,
        turn_model_output={
            **current_turn_state.player_one.turn_model_output,
            'moves': player_one_moves.get('moves', [])
        }
    )

    new_player_two = PlayerState.from_state(
        current_turn_state.player_two,
        turn_model_output={
            **current_turn_state.player_two.turn_model_output,
            'moves': player_two_moves.get('moves', [])
        }
    )

    # Create new turn state
    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=game_state.world,
        player_one=new_player_one,
        player_two=new_player_two,
        input_moves=all_moves
    )

    # Update turns dictionary with new turn state
    turns = dict(game_state.turns)
    turns[current_turn] = new_turn_state
    
    return (GameState.builder(game_state)
            .with_turns(turns)
            .build())

def main():    
    # Create a test configuration
    test_config = {
        'board_size': 5,
        'max_turns': 10,
        'num_players': 2,
        'player_one_config': {
            'name': 'Test_Player_One',
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        },
        'player_two_config': {
            'name': 'Test_Player_Two',
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        }
    }

    # Create initial game state (will have default units at (0,2) and (4,2))
    game_state = GameState.from_config(test_config)

    print("\n" + "="*80)
    print("1. Testing create_llm_world_representation")
    print("Expected: A JSON structure showing the game board state from Player 1's perspective")
    print("This should include: game info, board cells, and territory control information")
    print("="*80)
    world_rep = create_llm_world_representation(game_state, 1)
    print("\nActual World representation for Player 1:")
    print("Game Info:", json.dumps(world_rep['game_info'], indent=2))
    print("\nControlled Territories:", json.dumps(world_rep['board']['controlled_territories'], indent=2))
    print("\nSample of Board Cells (first 3):", json.dumps(dict(list(world_rep['board']['cells'].items())[:3]), indent=2))

    print("\n" + "="*80)
    print("2. Testing get_ai_moves")
    print("Expected: Two sets of moves, one from each AI player")
    print("Each move should contain 'source', 'destination', and 'units' fields")
    print("="*80)
    try:
        print("\nAttempting to get moves for Player 1:")
        player_one_moves = get_ai_moves(game_state, 1)
        print("\nPlayer 1 moves (should show movement commands):")
        print(json.dumps(player_one_moves, indent=2))
        
        print("\nAttempting to get moves for Player 2:")
        player_two_moves = get_ai_moves(game_state, 2)
        print("\nPlayer 2 moves (should show movement commands):")
        print(json.dumps(player_two_moves, indent=2))
    except Exception as e:
        print(f"❌ Error getting AI moves: {str(e)}")
        print("Expected format should be: {'moves': [{'source': [x,y], 'destination': [x,y], 'units': n}, ...]}")

    print("\n" + "="*80)
    print("3. Testing get_input_action")
    print("Expected: A new game state with processed and validated moves from both players")
    print("This should combine and validate moves from both AIs while respecting unit limitations")
    print("="*80)
    try:
        new_state = get_input_action(game_state, (0, 2))
        
        current_turn = new_state.turns[new_state.current_turn]
        print("\nProcessed moves summary:")
        print("\nPlayer 1 submitted moves (raw):", 
              json.dumps(current_turn.player_one.turn_model_output.get('moves', []), indent=2))        
        print("\nPlayer 2 submitted moves (raw):", 
              json.dumps(current_turn.player_two.turn_model_output.get('moves', []), indent=2))
        
    except Exception as e:
        print(f"❌ Error in input action: {str(e)}")
        print("Check if moves are valid and units are available at source positions")

if __name__ == "__main__":
    main()