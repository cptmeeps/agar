from typing import Dict, Any
from utils.game_utils import print_game_state
from game_state import GameState
from input_action import get_input_action
from move_action import move_action
from combat_action import combat_action
from spawn_action import spawn_action
from turn_end_action import turn_end_action
from utils.event_logger import GameEventLogger

def turn(game_state: GameState) -> GameState:
    logger = GameEventLogger()
    new_state = game_state
    
    # Log turn start
    logger.log_action("turn_start", new_state)
    
    # Get input actions first
    temp_state = get_input_action(new_state, (0, 0))
    if not new_state.is_valid_state_change(temp_state, 'input'):
        logger.log_error("input_validation", ValueError("Invalid state change"), new_state)
        return new_state
    new_state = temp_state

    # Process all moves first
    for hex_pos in game_state.world.keys():
        temp_state = move_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'move'):
            logger.log_error("move_validation", ValueError("Invalid state change"), new_state, {"position": hex_pos})
            continue
        new_state = temp_state

    # Then process all combat
    for hex_pos in game_state.world.keys():
        temp_state = combat_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'combat'):
            logger.log_error("combat_validation", ValueError("Invalid state change"), new_state, {"position": hex_pos})
            continue
        new_state = temp_state

    # Then process all spawns
    for hex_pos in game_state.world.keys():
        temp_state = spawn_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'spawn'):
            print(f"Warning: Invalid state change detected during spawn phase at {hex_pos}")
            continue
        new_state = temp_state
    
    # Finally process all turn end actions
    for hex_pos in game_state.world.keys():
        temp_state = turn_end_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'turn_end'):
            print(f"Warning: Invalid state change detected during turn end phase at {hex_pos}")
            continue
        new_state = temp_state
    
    # Log turn end
    logger.log_action("turn_end", new_state)
    
    # Log the final turn state
    logger.log_turn_state(new_state, new_state.turns[new_state.current_turn])
    
    # Update turn counter using from_state
    return GameState.from_state(new_state, current_turn=new_state.current_turn + 1)


def create_game_state(config: Dict[str, Any]) -> GameState:
    return GameState.from_config(config)

def run_game(game_state: GameState) -> GameState:
    logger = GameEventLogger()
    logger.log_action("game_start", game_state)

    while game_state.game_status != "game_over":
        game_state = turn(game_state)
        print_game_state(game_state)
    
    logger.log_action("game_end", game_state)
    return game_state

def main():
    # Create initial game state using config
    config = {
        'board_size': 5,
        'max_turns': 4,
        'num_players': 2,
        'end_criteria': {'type': 'elimination'},
        'player_one_config': {
            'turn_prompt_config': [
                {
                    'prompt_filepath': 'game_prompts.txt',
                    'template_params': {}
                }
            ]
        },
        'player_two_config': {
            'turn_prompt_config': [
                {
                    'prompt_filepath': 'game_prompts.txt',
                    'template_params': {}
                }
            ]
        }
    }
    initial_state = GameState.from_config(config)
    game_state = run_game(initial_state)
    print("Game Over")

if __name__ == "__main__":
  main()