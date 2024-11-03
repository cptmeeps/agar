from typing import Dict, Tuple, Any
from ..game_engine import GameState, get_ai_moves

def get_input_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get moves from both AIs
    player_one_moves = get_ai_moves(game_state, 1)
    player_two_moves = get_ai_moves(game_state, 2)
    
    # Combine and restructure moves by source hex
    all_moves = {}
    for move in player_one_moves['moves'] + player_two_moves['moves']:
        source = tuple(move['source'])  # Convert [q, r] to (q, r)
        if source not in all_moves:
            all_moves[source] = []
        all_moves[source].append({
            'destination': tuple(move['destination']),
            'units': move['units']
        })
    
    # Update game state with restructured moves
    return GameState(
        **{**game_state.__dict__, 'current_turn_input': {'moves': all_moves}}
    ) 