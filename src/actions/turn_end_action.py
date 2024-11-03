from typing import Dict, Tuple, Any
from ..game_engine import GameState

def turn_end_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Only process turn end logic once per turn (at first hex)
    if hex_pos != next(iter(game_state.world)):
        return game_state
    
    # Check if max turns reached
    if game_state.current_turn >= game_state.max_turns:
        return GameState(**{**game_state.__dict__, 'game_status': 'game_over'})
    
    # Count units for each player
    player_units = {i: 0 for i in range(1, game_state.num_players + 1)}
    for tile in game_state.world.values():
        for unit in tile.units:
            player_units[unit.player_id] += 1
    
    # Check if any player has been eliminated
    if any(count == 0 for count in player_units.values()):
        return GameState(**{**game_state.__dict__, 'game_status': 'game_over'})
    
    return game_state 