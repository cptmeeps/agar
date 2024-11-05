from typing import Dict, Any
from game_state import GameState
from utils.game_utils import print_game_state
from game_state import GameState
from actions.input_action import get_input_action
from actions.move_action import move_action
from actions.combat_action import combat_action
from actions.spawn_action import spawn_action
from actions.turn_end_action import turn_end_action

def turn(game_state: GameState) -> GameState:
    new_state = game_state
    print(f"Turn {new_state.current_turn}")
    print(f"Game status: {new_state.game_status}")
    # Get input actions first
    temp_state = get_input_action(new_state, (0, 0))
    if not new_state.is_valid_state_change(temp_state, 'input'):
        print("Warning: Invalid state change detected during input phase")
        return new_state
    new_state = temp_state
    
    # Process all moves first
    for hex_pos in game_state.world.keys():
        temp_state = move_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'move'):
            print(f"Warning: Invalid state change detected during move phase at {hex_pos}")
            continue
        new_state = temp_state
    
    # Then process all combat
    for hex_pos in game_state.world.keys():
        temp_state = combat_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'combat'):
            print(f"Warning: Invalid state change detected during combat phase at {hex_pos}")
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
    
    # Update turn counter using from_state
    return GameState.from_state(new_state, current_turn=new_state.current_turn + 1)

def create_game_state(config: Dict[str, Any]) -> GameState:
    return GameState.from_config(config)

def run_game(game_state: GameState) -> GameState:
    print_game_state(game_state)
    
    while game_state.game_status != "game_over":
        game_state = turn(game_state)
        print_game_state(game_state)
    
    return game_state

def main():
    # Create initial game state using config
    config = {
        'board_size': 5,
        'max_turns': 10,
        'num_players': 2,
        'end_criteria': {'type': 'elimination'},
        'player_one_config': {},
        'player_two_config': {}
    }
    initial_state = GameState.from_config(config)
    game_state = run_game(initial_state)
    print("Game Over")

if __name__ == "__main__":
  main()