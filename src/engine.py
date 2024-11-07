from typing import Dict, Any
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
    print("\n\n" + "=" * 60)
    # print("-" * 40)
    print("Turn: " + str(new_state.current_turn))

    
    # Get input actions first
    temp_state = get_input_action(new_state, (0, 0))
    if not new_state.is_valid_state_change(temp_state, 'input'):
        logger.log_error("input_validation", ValueError("Invalid state change"), new_state)
        return new_state
    new_state = temp_state

    # Print input actions summary
    current_turn_state = new_state.turns[new_state.current_turn]
    print("\nInput actions this turn:")
    print("-" * 40)
    print("p_id\tsrc\tdest\tunits")
    if current_turn_state.input_moves:
        for pos, moves in current_turn_state.input_moves.items():
            for player_id, player_moves in moves.items():
                for move in player_moves:
                    print(f"{player_id}\t{pos}\t{move['destination']}\t{move['units']}")
    else:
        print("No input actions")

    # Process all moves first
    for hex_pos in game_state.world.keys():
        temp_state = move_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'move'):
            logger.log_error("move_validation", ValueError("Invalid state change"), new_state, {"position": hex_pos})
            continue
        new_state = temp_state

    # Print moves summary
    current_turn_state = new_state.turns[new_state.current_turn]
    print("\nMoves this turn:")
    print("-" * 40)
    print("p_id\tsrc\tdest\tunits")
    if current_turn_state.move_actions:
        for move in current_turn_state.move_actions:
            print(f"{move['player_id']}\t{move['source']}\t{move['destination']}\t{move['units']}")

    # Then process all combat
    for hex_pos in game_state.world.keys():
        temp_state = combat_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'combat'):
            logger.log_error("combat_validation", ValueError("Invalid state change"), new_state, {"position": hex_pos})
            continue
        new_state = temp_state

    # Print combat summary
    current_turn_state = new_state.turns[new_state.current_turn]
    print("\nCombats this turn:")
    print("-" * 40)
    print("pos\tp1_cas\tp2_cas")
    if current_turn_state.combat_actions:
        for combat in current_turn_state.combat_actions:
            print(f"{combat['position']}\t{combat['player_1_casualties']}\t{combat['player_2_casualties']}")

    # Then process all spawns
    for hex_pos in game_state.world.keys():
        temp_state = spawn_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'spawn'):
            print(f"Warning: Invalid state change detected during spawn phase at {hex_pos}")
            continue
        new_state = temp_state
    
    # Print spawn summary
    current_turn_state = new_state.turns[new_state.current_turn]
    print(f"\nSpawns for turn {current_turn_state.turn_number}:")
    print("-" * 40)
    print("p_id\tposition")
    if current_turn_state.spawn_actions:
        for spawn in current_turn_state.spawn_actions:
            print(f"{spawn['player_id']}\t{spawn['position']}")
    
    # Finally process all turn end actions
    for hex_pos in game_state.world.keys():
        temp_state = turn_end_action(new_state, hex_pos)
        if not new_state.is_valid_state_change(temp_state, 'turn_end'):
            print(f"Warning: Invalid state change detected during turn end phase at {hex_pos}")
            continue
        new_state = temp_state
    
    # Log turn end
    logger.log_action("turn_end", new_state)
    
    # Print world summary
    new_state.print_world()

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
                    'prompt_filepath': 'expansion.txt',
                    'template_params': {}
                }
            ]
        },
        'player_two_config': {
            'turn_prompt_config': [
                {
                    'prompt_filepath': 'attack.txt',
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