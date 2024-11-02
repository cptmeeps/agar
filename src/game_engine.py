from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Type definitions
class TerrainType(Enum):
    PLAINS = "plains"

class UnitType(Enum):
    WARRIOR = "warrior"

@dataclass(frozen=True)
class Position:
    q: int  # axial coordinates
    r: int
    
    def __add__(self, other: 'Position') -> 'Position':
        return Position(self.q + other.q, self.r + other.r)

@dataclass(frozen=True)
class Unit:
    unit_type: UnitType
    player_id: int
    health: int
    movement_points: int

@dataclass(frozen=True)
class Tile:
    position: Position
    terrain: TerrainType
    units: List[Unit] = field(default_factory=list)

@dataclass(frozen=True)
class GameState:
    tiles: Dict[Tuple[int, int], Tile]
    current_player: int
    turn_number: int

def create_game_state(size: int) -> GameState:
    tiles = {}
    for q in range(-size, size + 1):
        r1 = max(-size, -q - size)
        r2 = min(size, -q + size)
        for r in range(r1, r2 + 1):
            pos = Position(q, r)
            tiles[(q, r)] = Tile(pos, TerrainType.PLAINS)
    
    return GameState(tiles=tiles, current_player=1, turn_number=1)

