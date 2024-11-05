from typing import Dict, Tuple, Any
from game_state import GameState, Tile, Unit

def spawn_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    tile = game_state.world[hex_pos]
    
    # Skip if no units in tile
    if not tile.units:
        return game_state
    
    # Group units by player
    players_units = {}
    for unit in tile.units:
        if unit.player_id not in players_units:
            players_units[unit.player_id] = []
        players_units[unit.player_id].append(unit)
    
    # Only spawn if one player controls the hex and has at least one unit
    if len(players_units) != 1:
        return game_state
        
    # print("players_units at", hex_pos, ":", players_units)
    player_id = list(players_units.keys())[0]
    if len(players_units[player_id]) < 1:
        return game_state
    # print(f"Turn {game_state.current_turn}: Spawning unit for player {player_id} at {hex_pos}")

    # Create new unit
    new_unit = Unit(
        player_id=player_id,
        health=1,
        movement_points=1
    )
    
    # Update world with new unit
    world = dict(game_state.world)
    world[hex_pos] = Tile(
        position=tile.position,
        units=list(tile.units) + [new_unit]
    )
    
    # Update turns dictionary with spawn information
    turns = dict(game_state.turns)
    current_turn_data = turns.get(game_state.current_turn, {})
    
    if 'spawns' not in current_turn_data:
        current_turn_data['spawns'] = []
    
    current_turn_data['spawns'].append({
        'hex': hex_pos,
        'player': player_id
    })
    
    turns[game_state.current_turn] = current_turn_data
    
    return GameState.from_state(game_state, world=world, turns=turns) 