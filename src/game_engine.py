from typing import Dict, Tuple, Any
import yaml
from game_types import GameState, Position, Tile
from input_action import get_input_action
from move_action import move_action
from combat_action import combat_action
from spawn_action import spawn_action
from turn_end_action import turn_end_action
from utils import create_sample_game_state, print_game_state

def turn(game_state: GameState) -> GameState:
  new_state = game_state
  
  new_state = get_input_action(new_state, (0, 0))
  
  for hex_pos in game_state.world.keys():
    new_state = move_action(new_state, hex_pos)
    new_state = combat_action(new_state, hex_pos)
    new_state = spawn_action(new_state, hex_pos)
    new_state = turn_end_action(new_state, hex_pos)
  
  return GameState(
    **{**new_state.__dict__, 'current_turn': new_state.current_turn + 1}
  )

def create_game_state(config: Dict[str, Any]) -> GameState:
  world = {}
  size = config.get('board_size', 5)
  
  # Create a rectangular grid
  for x in range(size):
    for y in range(size):
      pos = (x, y)
      world[pos] = Tile(Position(x, y))
  
  return GameState(
    world=world,
    current_turn=1,
    max_turns=config.get('max_turns', 100),
    num_players=config.get('num_players', 2),
    game_status="in_progress",
    game_end_criteria=config.get('end_criteria', {'type': 'elimination'})
  )

def run_game(config: Dict[str, Any]) -> GameState:
  game_state = create_game_state(config) if config else create_sample_game_state()
  print_game_state(game_state)
  
  while game_state.game_status != "game_over":
    game_state = turn(game_state)
    print_game_state(game_state)
  
  return game_state

def main():
  game_state = run_game(None)  # Pass None to use sample game state
  print("Game Over")

if __name__ == "__main__":
  main()