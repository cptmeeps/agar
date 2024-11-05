from typing import Dict, Tuple, Any
from game_state import GameState

def turn_end_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Only process turn end logic once per turn (at first hex)
    if hex_pos != next(iter(game_state.world)):
        return game_state
    
    # Check if max turns reached
    if game_state.current_turn >= game_state.max_turns:
        print(f"Game Over: Maximum turns ({game_state.max_turns}) reached")
        return GameState.from_state(game_state, game_status='game_over')
    
    # Count units for each player
    player_units = {i: 0 for i in range(1, game_state.num_players + 1)}
    for tile in game_state.world.values():
        for unit in tile.units:
            player_units[unit.player_id] += 1
    
    # Check if any player has been eliminated
    if any(count == 0 for count in player_units.values()):
        eliminated_players = [player_id for player_id, count in player_units.items() if count == 0]
        print(f"Game Over: Player(s) {eliminated_players} eliminated (no units remaining)")
        return GameState.from_state(game_state, game_status='game_over')
    
    return game_state 