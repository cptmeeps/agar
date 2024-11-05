from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any

@dataclass(frozen=True)
class Position:
    x: int 
    y: int
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.x + other.x, self.y + other.y)

@dataclass(frozen=True)
class Unit:
  player_id: int
  health: int
  movement_points: int

@dataclass(frozen=True)
class Tile:
  position: Position
  units: List[Unit] = field(default_factory=list)