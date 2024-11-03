from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

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