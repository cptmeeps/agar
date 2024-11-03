from typing import Dict, Tuple, Any
import yaml
from .game_types import GameState, Position, Tile
from .actions import (
  get_input_action,
  move_action,
  combat_action,
  spawn_action,
  turn_end_action
)

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
  
  for q in range(-size, size + 1):
    r1 = max(-size, -q - size)
    r2 = min(size, -q + size)
    for r in range(r1, r2 + 1):
      pos = (q, r)
      world[pos] = Tile(Position(q, r))
  
  return GameState(
    world=world,
    current_turn=1,
    max_turns=config.get('max_turns', 100),
    num_players=config.get('num_players', 2),
    game_status="in_progress",
    game_end_criteria=config.get('end_criteria', {'type': 'elimination'})
  )

def run_game(config: Dict[str, Any]) -> Tuple[GameState, str]:
  game_state = create_game_state(config)
  
  while game_state.game_status != "game_over":
    game_state = turn(game_state)
  
  return game_state

def main():
  config = {
    'board_size': 5,
    'max_turns': 100,
    'num_players': 2,
    'end_criteria': {
      'type': 'elimination',
      'turn_limit': 100
    }
  }
  
  game_state = run_game(config)
  print("Game Over")

if __name__ == "__main__":
  main()