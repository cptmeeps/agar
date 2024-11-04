from utils import create_sample_game_state, print_game_state
from game_engine import run_game
from input_action import create_llm_world_representation, get_ai_moves, get_input_action
import yaml
import json

def test_run_game():
  print("Starting game test...")
  # Create and display initial game state
  # print("\nInitial Game State:")
  game_state = create_sample_game_state()
  # print_game_state(game_state)
  
  # Run the game and get final state
  print("\nRunning game simulation...")
  final_state = run_game(game_state)
  
  # Display final state
  print("\nFinal Game State:")
  print_game_state(final_state)
  
  print(f"\nGame completed with status: {final_state.game_status}")
  return final_state

def test_world_representation():
    print("Testing LLM world representation...")
    # Create sample game state
    game_state = create_sample_game_state()
    
    # Get world representation for both players
    print("\nWorld representation for Player 1:")
    world_rep_p1 = create_llm_world_representation(game_state, player_id=1)
    print(yaml.dump(world_rep_p1, sort_keys=False))
    
    print("\nWorld representation for Player 2:")
    world_rep_p2 = create_llm_world_representation(game_state, player_id=2)
    print(yaml.dump(world_rep_p2, sort_keys=False))
    
    return world_rep_p1, world_rep_p2

def test_ai_moves():
    print("Testing AI moves generation...")
    # Create sample game state
    game_state = create_sample_game_state()
    
    # Get AI moves for both players
    print("\nAI moves for Player 1:")
    moves_p1 = get_ai_moves(game_state, player_id=1)
    print(yaml.dump(moves_p1, sort_keys=False))
    
    print("\nAI moves for Player 2:")
    moves_p2 = get_ai_moves(game_state, player_id=2)
    print(yaml.dump(moves_p2, sort_keys=False))
    
    return moves_p1, moves_p2

def test_input_action():
    print("Testing input action generation...")
    # Create sample game state
    game_state = create_sample_game_state()
    
    # Get combined moves through input action
    print("\nGetting combined moves for both players:")
    updated_state = get_input_action(game_state, (0, 0))
    print_game_state(updated_state)
    return updated_state

if __name__ == "__main__":
  test_run_game()
  # # print("\n" + "="*50 + "\n")
  # # test_world_representation()
  # # print("\n" + "="*50 + "\n")
  # # test_ai_moves()
  # # print("\n" + "="*50 + "\n")
  # test_input_action()