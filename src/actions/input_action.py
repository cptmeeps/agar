from typing import Dict, Tuple, Any
import yaml
from game_state import GameState, create_sample_game_state
from llm import create_message_chain, call_llm_api, load_game_prompts
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
            prompt_path="src/prompts/game_prompts.txt",
            variables={'world_representation': world_representation}
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Error creating message chain: {e}")
        return {"moves": []}
    
    # Get LLM response
    response = call_llm_api(message_chain)
    try:
        response = json.loads(response)
        return response
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error parsing moves: {e}")
    
    return {}

def get_input_action(game_state: GameState, cell_pos: Tuple[int, int]) -> GameState:
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
            
            # Skip if source position doesn't exist in world
            if source_pos not in game_state.world:
                continue
                
            # Initialize source position in all_moves if needed
            if source_pos not in all_moves:
                all_moves[source_pos] = {1: [], 2: []}
            
            # Calculate available units for this move
            available_units = remaining_units[source_pos][source]
            
            # Skip if no units available
            if available_units <= 0:
                continue
                
            # Adjust units to move based on availability
            units_to_move = min(move['units'], available_units)
            
            # Update remaining units
            remaining_units[source_pos][source] -= units_to_move
            
            # Add valid move to all_moves
            all_moves[source_pos][source].append({
                'destination': tuple(move['destination']),
                'units': units_to_move
            })
    
    # Create or update turn data in turns dictionary
    turns = dict(game_state.turns)
    turns[game_state.current_turn] = {
        'turn_input': {'moves': all_moves}
    }
    
    # Create new game state with updated turns
    return GameState(
        world=game_state.world,
        current_turn=game_state.current_turn,
        max_turns=game_state.max_turns,
        num_players=game_state.num_players,
        game_status=game_state.game_status,
        game_end_criteria=game_state.game_end_criteria,
        player_one_config=game_state.player_one_config,
        player_two_config=game_state.player_two_config,
        turns=turns
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