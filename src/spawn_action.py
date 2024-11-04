from typing import Dict, Tuple, Any
from game_types import GameState, Tile, Unit

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
    
    # Update turns dictionary with spawn information
    turns = dict(game_state.turns)
    current_turn_data = turns.get(game_state.current_turn, {})
    
    # Initialize or get existing spawns list
    if 'spawns' not in current_turn_data:
        current_turn_data['spawns'] = []
    
    # Add spawn information, in the format:
    # turns = {
    #     1: {
    #         'turn_input': {...},
    #         'spawns': [
    #             {'hex': (0, 2), 'player': 1},
    #             {'hex': (3, 1), 'player': 2}
    #         ]
    #     }
    # }

    current_turn_data['spawns'].append({
        'hex': hex_pos,
        'player': player_id
    })
    
    # Update turns dictionary
    turns[game_state.current_turn] = current_turn_data
    
    return GameState(
        world=world,
        current_turn=game_state.current_turn,
        max_turns=game_state.max_turns,
        num_players=game_state.num_players,
        game_status=game_state.game_status,
        game_end_criteria=game_state.game_end_criteria,
        player_one_config=game_state.player_one_config,
        player_two_config=game_state.player_two_config,
        turns=turns
    ) 