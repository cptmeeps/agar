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
    
    # Create combat record
    combat_record = {
        'position': hex_pos,
        'player_1_casualties': damage_dealt.get(1, 0),
        'player_2_casualties': damage_dealt.get(2, 0)
    }
    
    # Update turn state
    turns = dict(game_state.turns)
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]
    
    # Update player states using from_state
    new_player_one = PlayerState.from_state(
        current_turn_state.player_one,
        turn_model_output={
            **current_turn_state.player_one.turn_model_output,
            'combats': [*current_turn_state.player_one.turn_model_output.get('combats', []), combat_record]
        }
    )

    new_player_two = PlayerState.from_state(
        current_turn_state.player_two,
        turn_model_output={
            **current_turn_state.player_two.turn_model_output,
            'combats': [*current_turn_state.player_two.turn_model_output.get('combats', []), combat_record]
        }
    )

    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=world,
        player_one=new_player_one,
        player_two=new_player_two,
        combat_actions=[*current_turn_state.combat_actions, combat_record]
    )
    
    turns[current_turn] = new_turn_state
    
    # Use builder to create new state
    return (GameState.builder(game_state)
            .with_world(world)
            .with_turns(turns)
            .build())
    
    # Log combat results
    logger.log_combat(
        game_state,
        hex_pos,
        damage_dealt
    )
    
    return GameState.from_state(game_state, world=world, turns=turns) 