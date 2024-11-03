from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto
import yaml
from .actions import (
    get_input_action,
    move_action,
    combat_action,
    spawn_action,
    turn_end_action
)

@dataclass(frozen=True)
class Position:
  q: int 
  r: int
  
  def __add__(self, other: 'Position') -> 'Position':
    return Position(self.q + other.q, self.r + other.r)

@dataclass(frozen=True)
class Unit:
  player_id: int
  health: int
  movement_points: int

@dataclass(frozen=True)
class Tile:
  position: Position
  units: List[Unit] = field(default_factory=list)

@dataclass(frozen=True)
class GameState:
  world: Dict[Tuple[int, int], Tile]
  current_turn: int
  max_turns: int
  num_players: int
  game_status: str
  game_end_criteria: Dict[str, Any]
  player_one_config: Dict[str, Any]
  player_two_config: Dict[str, Any]
  turns: Dict[int, Dict[str, Any]]
  current_turn_input: Dict[str, Any]

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

def run_game(config: Dict[str, Any]) -> Tuple[GameState, str]:
  game_state = create_game_state(config)
  
  while game_state.game_status != "game_over":
    game_state = turn(game_state)
  
  return game_state

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

def create_llm_world_representation(game_state: GameState, player_id: int) -> Dict[str, Any]:
    """
    Creates a player-specific structured representation of the game world for LLM consumption.
    
    Args:
        game_state: Current state of the game
        player_id: The player (1 or 2) for whom this representation is being created
    """
    opponent_id = 2 if player_id == 1 else 1
    
    world_representation = {
        "game_info": {
            "current_turn": game_state.current_turn,
            "max_turns": game_state.max_turns,
            "game_status": game_state.game_status
        },
        "board": {
            "controlled_territories": {
                "your_territory": [],
                "enemy_territory": []
            },
            "hexes": []
        }
    }

    # Process each hex
    for pos, tile in game_state.world.items():
        q, r = pos
        
        # Group units by player
        units_count = {
            "your_units": 0,
            "enemy_units": 0
        }
        
        # Count units
        for unit in tile.units:
            if unit.player_id == player_id:
                units_count["your_units"] += 1
            else:
                units_count["enemy_units"] += 1

        # Determine hex control
        controlling_player = None
        if units_count["your_units"] > 0 and units_count["enemy_units"] == 0:
            controlling_player = "you"
            world_representation["board"]["controlled_territories"]["your_territory"].append(
                {"q": q, "r": r}
            )
        elif units_count["enemy_units"] > 0 and units_count["your_units"] == 0:
            controlling_player = "enemy"
            world_representation["board"]["controlled_territories"]["enemy_territory"].append(
                {"q": q, "r": r}
            )

        # Create hex representation
        hex_info = {
            "position": {"q": q, "r": r},
            "units": units_count,
            "controlled_by": controlling_player
        }
        world_representation["board"]["hexes"].append(hex_info)

    return world_representation

def create_llm_world_representation(game_state: GameState, player_id: int) -> Dict[str, Any]:
    opponent_id = 2 if player_id == 1 else 1
    
    world_representation = {
        "game_info": {
            "current_turn": game_state.current_turn,
            "max_turns": game_state.max_turns,
            "game_status": game_state.game_status
        },
        "board": {
            "controlled_territories": {
                "your_territory": [],
                "enemy_territory": []
            },
            "hexes": []
        }
    }

    # Process each hex
    for pos, tile in game_state.world.items():
        q, r = pos
        
        # Group units by player
        units_count = {
            "your_units": 0,
            "enemy_units": 0
        }
        
        # Count units
        for unit in tile.units:
            if unit.player_id == player_id:
                units_count["your_units"] += 1
            else:
                units_count["enemy_units"] += 1

        # Determine hex control
        controlling_player = None
        if units_count["your_units"] > 0 and units_count["enemy_units"] == 0:
            controlling_player = "you"
            world_representation["board"]["controlled_territories"]["your_territory"].append(
                {"q": q, "r": r}
            )
        elif units_count["enemy_units"] > 0 and units_count["your_units"] == 0:
            controlling_player = "enemy"
            world_representation["board"]["controlled_territories"]["enemy_territory"].append(
                {"q": q, "r": r}
            )

        # Create hex representation
        hex_info = {
            "position": {"q": q, "r": r},
            "units": units_count,
            "controlled_by": controlling_player
        }
        world_representation["board"]["hexes"].append(hex_info)

    return world_representation

def create_strategic_prompt(game_state: GameState, player_id: int) -> Dict[str, Any]:
    # Get the world representation
    world_representation = create_llm_world_representation(game_state, player_id)
    
    # Load and prepare the prompt template
    prompt_template = load_game_prompts()
    game_state_yaml = yaml.dump(world_representation, sort_keys=False)
    
    return {
        'template': prompt_template,
        'variables': {'game_state_yaml': game_state_yaml}
    }

def get_ai_moves(game_state: GameState, player_id: int) -> Dict[str, Any]:
    from llm import create_message_chain, call_llm_api
    
    # Create game state representation
    world_representation = create_llm_world_representation(game_state, player_id)
    game_state_yaml = yaml.dump(world_representation, sort_keys=False)
    
    # Create message chain with game state
    try:
        message_chain = create_message_chain(
            prompt_path="src/prompts/game_prompts.yaml",
            variables={'game_state_yaml': game_state_yaml}
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Error creating message chain: {e}")
        return {"moves": []}
    
    # Get and parse LLM response
    response = call_llm_api(message_chain)
    try:
        moves = yaml.safe_load(response)
        return moves
    except yaml.YAMLError:
        return {"moves": []}

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

