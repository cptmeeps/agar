from typing import Dict, Tuple, Any
from game_state import GameState
from utils.logger import logger

def turn_end_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    if hex_pos != next(iter(game_state.world)):
        return game_state
    
    if game_state.current_turn >= game_state.max_turns:
        logger.log_action(
            "game_over",
            game_state,
            details={"reason": "max_turns_reached"}
        )
        return GameState.from_state(game_state, game_status='game_over')
    
    player_units = {i: 0 for i in range(1, game_state.num_players + 1)}
    for tile in game_state.world.values():
        for unit in tile.units:
            player_units[unit.player_id] += 1
    
    if any(count == 0 for count in player_units.values()):
        eliminated_players = [player_id for player_id, count in player_units.items() if count == 0]
        logger.log_action(
            "game_over",
            game_state,
            details={
                "reason": "player_eliminated",
                "eliminated_players": eliminated_players
            }
        )
        return GameState.from_state(game_state, game_status='game_over')
    
    logger.log_action(
        "turn_end",
        game_state,
        details={"unit_counts": player_units}
    )
    
    return game_state