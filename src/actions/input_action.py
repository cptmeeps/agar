from typing import Dict, Tuple, Any
from game_state import GameState, Tile, PlayerState, TurnState
from utils.llm import create_message_chain, call_llm_api
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
    try:
        message_chain = create_message_chain(
            prompt_path="src/prompts/game_prompts.txt",
            variables={'world_representation': world_representation}
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        logger.log_error(
            "ai_move_generation",
            e,
            game_state,
            {"player_id": player_id}
        )
        return {"moves": []}
    
    # Get LLM response
    response = call_llm_api(message_chain)
    try:
        response = json.loads(response)
        logger.log_action(
            "ai_move_generation",
            game_state,
            details={"player_id": player_id, "moves": response.get("moves", [])}
        )
        return response
    except (json.JSONDecodeError, AttributeError) as e:
        logger.log_error(
            "ai_move_parsing",
            e,
            game_state,
            {"player_id": player_id, "raw_response": response}
        )
    
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

    # Get current turn state
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]
    
    # Create new turn state with player states including the moves
    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=game_state.world,
        player_one=PlayerState(
            player_config=current_turn_state.player_one.player_config,
            turn_msg_chain=current_turn_state.player_one.turn_msg_chain,
            turn_model_output=current_turn_state.player_one.turn_model_output,
            turn_input={}
        ),
        player_two=PlayerState(
            player_config=current_turn_state.player_two.player_config,
            turn_msg_chain=current_turn_state.player_two.turn_msg_chain,
            turn_model_output=current_turn_state.player_two.turn_model_output,
            turn_input={}
        ),
        input_moves=all_moves
    )

    # Update turns dictionary
    turns = dict(game_state.turns)
    turns[current_turn] = new_turn_state
    
    return GameState.from_state(game_state, turns=turns)