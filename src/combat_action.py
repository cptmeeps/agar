from typing import Dict, Tuple, Any
import random
from game_types import GameState, Tile

def combat_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # If no units or only one player's units, skip combat
    tile = game_state.world[hex_pos]
    if len(tile.units) <= 1:
        return game_state
    
    # Group units by player
    players_units = {}
    for unit in tile.units:
        if unit.player_id not in players_units:
            players_units[unit.player_id] = []
        players_units[unit.player_id].append(unit)
    
    # If units from only one player, no combat
    if len(players_units) <= 1:
        return game_state
    
    # Store initial unit counts and calculate damage
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
    
    return GameState(**{**game_state.__dict__, 'world': world}) 