from typing import Dict, Tuple, Any
import yaml
from game_types import GameState
from llm import create_message_chain, call_llm_api, load_game_prompts
from utils import create_sample_game_state
import json

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
    try:
        message_chain = create_message_chain(
            prompt_path="prompts/game_prompts.txt",
            variables={'world_representation': world_representation}
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Error creating message chain: {e}")
        return {"moves": []}
    
    # Get LLM response
    response = call_llm_api(message_chain)
    # print(f"Response: {response}")
    try:
        response = json.loads(response)
        # print(f"Response: {response}")
        return response
        # return response.get('moves', {})
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing moves: {e}")
    
    return {"moves": []}

def get_input_action(game_state: GameState, cell_pos: Tuple[int, int]) -> GameState:
    # Get moves from both AIs
    player_one_moves = get_ai_moves(game_state, 1)
    player_two_moves = get_ai_moves(game_state, 2)
    
    # Restructure moves by source cell, keeping players separate
    all_moves = {}
    for source, player_moves in [
        (1, player_one_moves['moves']), 
        (2, player_two_moves['moves'])
    ]:
        for move in player_moves:
            source_pos = tuple(move['source'])  # Convert [q, r] to (q, r)
            if source_pos not in all_moves:
                all_moves[source_pos] = {1: [], 2: []}
            all_moves[source_pos][source].append({
                'destination': tuple(move['destination']),
                'units': move['units']
            })
    
    # Update game state with restructured moves
    return GameState(
        **{**game_state.__dict__, 'current_turn_input': {'moves': all_moves}}
    )

def main():
    # Create sample game state
    game_state = create_sample_game_state()
    print("\n1. Created sample game state")
    
    # Test create_llm_world_representation
    world_rep = create_llm_world_representation(game_state, player_id=1)
    print("\n2. World representation for player 1:")
    print(yaml.dump(world_rep, sort_keys=False))
    
    
    # Test get_ai_moves
    moves = get_ai_moves(game_state, player_id=1)
    print("\n4. AI moves generated:")
    print(yaml.dump(moves, sort_keys=False))
    
    # Test get_input_action
    updated_state = get_input_action(game_state, (0, 0))
    print("\n5. Final game state after input action:")
    print(f"Current turn input: {updated_state.current_turn_input}")

if __name__ == "__main__":
    main() 