from typing import Dict, Tuple, Any
import yaml
from game_types import GameState, Position, Tile, Unit
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
    # Create a simple 5x5 world with some units
    world = {}
    size = config.get('board_size', 5)
    
    for x in range(size):
        for y in range(size):
            pos = (x, y)
            units = []
            # Add player 1's unit at (0, 2) - left side
            if x == 0 and y == 2:
                units = [Unit(player_id=1, health=1, movement_points=1)]
            # Add player 2's unit at (4, 2) - right side
            elif x == size-1 and y == 2:
                units = [Unit(player_id=2, health=1, movement_points=1)]
            
            world[pos] = Tile(Position(x, y), units)
    
    return GameState(
        world=world,
        current_turn=1,
        max_turns=config.get('max_turns', 10),
        num_players=config.get('num_players', 2),
        game_status="in_progress",
        game_end_criteria=config.get('end_criteria', {'type': 'elimination'}),
        player_one_config=config.get('player_one_config', {}),
        player_two_config=config.get('player_two_config', {}),
        turns={},
        current_turn_input={}
    )

def run_game(game_state: GameState) -> GameState:
    print_game_state(game_state)
    
    while game_state.game_status != "game_over":
        game_state = turn(game_state)
        print_game_state(game_state)
    
    return game_state

def main():
    # Create initial game state using sample state
    initial_state = create_sample_game_state()
    game_state = run_game(initial_state)
    print("Game Over")

if __name__ == "__main__":
  main()