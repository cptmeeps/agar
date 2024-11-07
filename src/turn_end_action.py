from typing import Dict, Tuple, Any
from game_state import GameState, TurnState, Tile
from utils.logger import logger

def turn_end_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    if hex_pos != next(iter(game_state.world)):
        return game_state
    
    # Calculate scores for current turn
    scores = game_state.calculate_scores()
    
    # Update both the turn state and game state scores
    turns = dict(game_state.turns)
    current_turn_state = turns[game_state.current_turn]
    turns[game_state.current_turn] = TurnState(
        **{**current_turn_state.__dict__, 'scores': scores}
    )
    
    # Create new game state with updated scores
    new_game_state = GameState.from_state(
        game_state,
        turns=turns,
        scores=scores  # Update the root scores
    )
    
    if game_state.current_turn >= game_state.max_turns:
        logger.log_action(
            "game_over",
            new_game_state,
            details={
                "reason": "max_turns_reached",
                "final_scores": scores
            }
        )
        return GameState.from_state(
            new_game_state, 
            game_status='game_over'
        )
    
    player_units = {i: 0 for i in range(1, game_state.num_players + 1)}
    for tile in game_state.world.values():
        for unit in tile.units:
            player_units[unit.player_id] += 1
    
    if any(count == 0 for count in player_units.values()):
        eliminated_players = [player_id for player_id, count in player_units.items() if count == 0]
        logger.log_action(
            "game_over",
            new_game_state,
            details={
                "reason": "player_eliminated",
                "eliminated_players": eliminated_players,
                "final_scores": scores
            }
        )
        return GameState.from_state(
            new_game_state, 
            game_status='game_over'
        )
    
    logger.log_action(
        "turn_end",
        new_game_state,
        details={
            "unit_counts": player_units,
            "scores": scores
        }
    )
    
    return GameState.from_state(new_game_state)

def main():
    # Create a test configuration
    test_config = {
        'board_size': 5,
        'max_turns': 3,  # Small number to test max turns condition
        'num_players': 2,
        'player_one_config': {
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        },
        'player_two_config': {
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        }
    }

    # Create initial game state
    game_state = GameState.from_config(test_config)

    print("\n" + "="*80)
    print("Testing turn_end_action")
    print("Expected: Process end of turn and check various end conditions")
    print("="*80)

    # Test 1: Normal turn end
    print("\n1. Testing normal turn end")
    print("Initial state:")
    print(f"Current turn: {game_state.current_turn}")
    print(f"Game status: {game_state.game_status}")
    
    new_state = turn_end_action(game_state, (0, 2))
    print("\nAfter turn end:")
    print(f"Current turn: {new_state.current_turn}")
    print(f"Game status: {new_state.game_status}")


if __name__ == "__main__":
    main()