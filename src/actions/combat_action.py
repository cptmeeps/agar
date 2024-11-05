from typing import Dict, Tuple, Any
import random
from game_state import GameState, Tile, PlayerState, TurnState
from utils.logger import logger

def combat_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    tile = game_state.world[hex_pos]
    if len(tile.units) <= 1:
        return game_state
    
    players_units = {}
    for unit in tile.units:
        if unit.player_id not in players_units:
            players_units[unit.player_id] = []
        players_units[unit.player_id].append(unit)
    
    if len(players_units) <= 1:
        return game_state
    
    initial_counts = {player_id: len(units) for player_id, units in players_units.items()}
    damage_dealt = {player_id: 0 for player_id in players_units.keys()}
    
    # Combat rolls - each player rolls once
    for player_id in players_units.keys():
        roll = random.randint(1, 10)
        if roll > 4:  # Success on 5 or higher (60% chance)
            # Calculate damage based on initial unit count
            for other_player_id in players_units.keys():
                if other_player_id != player_id:
                    damage_dealt[other_player_id] += initial_counts[player_id]
    
    # Apply damage to all players
    surviving_units = []
    for player_id, units in players_units.items():
        # Keep only surviving units
        survivors = units[damage_dealt[player_id]:]
        surviving_units.extend(survivors)
    
    # Update the world with surviving units
    world = dict(game_state.world)
    world[hex_pos] = Tile(
        position=tile.position,
        units=surviving_units
    )
    
    # Get current turn state and create updated version
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]
    
    # Create combat record
    combat_record = {
        'position': hex_pos,
        'player_1_casualties': damage_dealt.get(1, 0),
        'player_2_casualties': damage_dealt.get(2, 0)
    }
    
    # Create new turn state with updated world and combat information
    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=world,
        player_one=PlayerState(
            player_config=current_turn_state.player_one.player_config,
            turn_msg_chain=current_turn_state.player_one.turn_msg_chain,
            turn_model_output={
                **current_turn_state.player_one.turn_model_output,
                'combats': [*current_turn_state.player_one.turn_model_output.get('combats', []), combat_record]
            },
            turn_input=current_turn_state.player_one.turn_input
        ),
        player_two=PlayerState(
            player_config=current_turn_state.player_two.player_config,
            turn_msg_chain=current_turn_state.player_two.turn_msg_chain,
            turn_model_output={
                **current_turn_state.player_two.turn_model_output,
                'combats': [*current_turn_state.player_two.turn_model_output.get('combats', []), combat_record]
            },
            turn_input=current_turn_state.player_two.turn_input
        )
    )
    
    # Update turns dictionary
    turns = dict(game_state.turns)
    turns[current_turn] = new_turn_state
    
    # Log combat results
    logger.log_combat(
        game_state,
        hex_pos,
        damage_dealt
    )
    
    return GameState.from_state(game_state, world=world, turns=turns) 