from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto
import random

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

def get_input_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
  # Get moves from both AIs
  player_one_moves = get_ai_moves(game_state, 1)
  player_two_moves = get_ai_moves(game_state, 2)
  
  # Combine and restructure moves by source hex
  all_moves = {}
  for move in player_one_moves['moves'] + player_two_moves['moves']:
    source = tuple(move['source'])  # Convert [q, r] to (q, r)
    if source not in all_moves:
      all_moves[source] = []
    all_moves[source].append({
      'destination': tuple(move['destination']),  # Convert [q, r] to (q, r)
      'units': move['units']
    })
  
  # Update game state with restructured moves
  return GameState(
    **{**game_state.__dict__, 'current_turn_input': {'moves': all_moves}}
  )

def move_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
  # If no moves exist or this hex isn't a source of any moves, return unchanged
  if ('moves' not in game_state.current_turn_input or 
    hex_pos not in game_state.current_turn_input['moves']):
    return game_state
  
  world = dict(game_state.world)
  moves = game_state.current_turn_input['moves'][hex_pos]
  source_tile = world[hex_pos]
  
  # Process each move from this source hex
  for move in moves:
    dest_pos = move['destination']
    units_to_move = move['units']
    
    # Skip if destination isn't valid
    if dest_pos not in world:
      continue
      
    # Skip if not enough units available
    if len(source_tile.units) < units_to_move:
      continue
    
    # Move units from source to destination
    moving_units = source_tile.units[:units_to_move]
    remaining_units = source_tile.units[units_to_move:]
    
    # Update source tile
    world[hex_pos] = Tile(
      position=source_tile.position,
      units=remaining_units
    )
    
    # Update destination tile
    dest_tile = world[dest_pos]
    world[dest_pos] = Tile(
      position=dest_tile.position,
      units=list(dest_tile.units) + moving_units
    )
  
  return GameState(**{**game_state.__dict__, 'world': world})

def combat_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
  # If no units or only one player's units, skip combat
  tile = game_state.world[hex_pos]
  if len(tile.units) <= 1:
    return game_state
  
  # Group units by player
  players_units = {}
  for unit in tile.units:
    if unit.player_id not in players_units:
      players_units[unit.player_id] = []
    players_units[unit.player_id].append(unit)
  
  # If units from only one player, no combat
  if len(players_units) <= 1:
    return game_state
  
  # Store initial unit counts and calculate damage
  initial_counts = {player_id: len(units) for player_id, units in players_units.items()}
  damage_dealt = {player_id: 0 for player_id in players_units.keys()}
  
  # Combat rolls - each player rolls once
  for player_id in players_units.keys():
    roll = random.randint(1, 10)
    if roll > 4:  # Success on 5 or higher (60% chance)
      # Calculate damage based on initial unit count
      for other_player_id in players_units.keys():
        if other_player_id != player_id:
          damage_dealt[other_player_id] += initial_counts[player_id]
  
  # Apply damage to all players
  surviving_units = []
  for player_id, units in players_units.items():
    # Keep only surviving units
    survivors = units[damage_dealt[player_id]:]
    surviving_units.extend(survivors)
  
  # Update the world with surviving units
  world = dict(game_state.world)
  world[hex_pos] = Tile(
    position=tile.position,
    units=surviving_units
  )
  
  return GameState(**{**game_state.__dict__, 'world': world})

def spawn_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
  tile = game_state.world[hex_pos]
  
  # Skip if no units in tile
  if not tile.units:
    return game_state
  
  # Group units by player
  players_units = {}
  for unit in tile.units:
    if unit.player_id not in players_units:
      players_units[unit.player_id] = []
    players_units[unit.player_id].append(unit)
  
  # Only spawn if one player controls the hex
  if len(players_units) != 1:
    return game_state
  
  # Get the controlling player and create new unit
  player_id = list(players_units.keys())[0]
  new_unit = Unit(
    player_id=player_id,
    health=1,
    movement_points=1
  )
  
  # Update world with new unit
  world = dict(game_state.world)
  world[hex_pos] = Tile(
    position=tile.position,
    units=list(tile.units) + [new_unit]
  )
  
  return GameState(**{**game_state.__dict__, 'world': world})

def turn_end_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
  # Only process turn end logic once per turn (at first hex)
  if hex_pos != next(iter(game_state.world)):
    return game_state
    
  # Check if max turns reached
  if game_state.current_turn >= game_state.max_turns:
    return GameState(**{**game_state.__dict__, 'game_status': 'game_over'})
  
  # Count units for each player
  player_units = {i: 0 for i in range(1, game_state.num_players + 1)}
  for tile in game_state.world.values():
    for unit in tile.units:
      player_units[unit.player_id] += 1
  
  # Check if any player has been eliminated
  if any(count == 0 for count in player_units.values()):
    return GameState(**{**game_state.__dict__, 'game_status': 'game_over'})
  
  return game_state

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

