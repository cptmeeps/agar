from typing import Dict, Tuple, Any
from ..game_engine import GameState, Tile, Unit

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
    
    # Only spawn if one player controls the hex
    if len(players_units) != 1:
        return game_state
    
    # Get the controlling player and create new unit
    player_id = list(players_units.keys())[0]
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
    
    return GameState(**{**game_state.__dict__, 'world': world}) 