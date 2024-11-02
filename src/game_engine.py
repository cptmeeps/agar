# Strategy game built using functional programming principles in Python.

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum, auto
import random
from anthropic import Anthropic
import os

# Type definitions
class TerrainType(Enum):
    PLAINS = "plains"

class UnitType(Enum):
    WARRIOR = "warrior"

class Phase(Enum):
    MOVEMENT = auto()
    COMBAT = auto()
    SPAWN = auto()

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
class TurnState:
    phase: Phase

@dataclass(frozen=True)
class GameState:
    world: Dict[Tuple[int, int], Tile]
    current_turn: int
    max_turns: int
    num_players: int
    current_phase: str
    game_end_criteria: Dict[str, Any]
    # Add any other state you want to track

class Action:
    def apply(self, game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
        raise NotImplementedError("Action must implement apply()")

class MoveAction(Action):
    def apply(self, game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
        # Implementation for movement
        pass

class CombatAction(Action):
    def apply(self, game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
        # Implementation for combat
        pass

class SpawnAction(Action):
    def apply(self, game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
        # Implementation for spawning
        pass

class Phase:
    def __init__(self, name: str, actions: List[Action]):
        self.name = name
        self.actions = actions
    
    def execute(self, game_state: GameState) -> GameState:
        new_state = game_state
        for hex_pos in game_state.world.keys():
            for action in self.actions:
                new_state = action.apply(new_state, hex_pos)
        return new_state

def create_game_state(config: Dict[str, Any]) -> GameState:
    # Create initial game state based on config
    world = {}
    size = config.get('board_size', 5)
    
    # Create hexagonal board
    for q in range(-size, size + 1):
        r1 = max(-size, -q - size)
        r2 = min(size, -q + size)
        for r in range(r1, r2 + 1):
            pos = (q, r)
            world[pos] = Tile(Position(q, r), TerrainType.PLAINS)
    
    return GameState(
        world=world,
        current_turn=1,
        max_turns=config.get('max_turns', 100),
        num_players=config.get('num_players', 2),
        current_phase='movement',
        game_end_criteria=config.get('end_criteria', {'type': 'elimination'})
    )

def turn(game_state: GameState, phases: List[Phase]) -> GameState:
    new_state = game_state
    
    for phase in phases:
        new_state = phase.execute(new_state)
        # Update current phase
        new_state = GameState(
            **{**new_state.__dict__, 'current_phase': phase.name}
        )
    
    # Increment turn counter
    return GameState(
        **{**new_state.__dict__, 'current_turn': new_state.current_turn + 1}
    )

def is_game_over(game_state: GameState) -> Tuple[bool, str]:
    # Implementation based on game_state.game_end_criteria
    pass

def run_game(config: Dict[str, Any]) -> Tuple[GameState, str]:
    # Create initial game state
    game_state = create_game_state(config)
    
    # Define phases with their actions
    game_phases = [
        Phase('movement', [MoveAction()]),
        Phase('combat', [CombatAction()]),
        Phase('spawn', [SpawnAction()])
    ]
    
    # Main game loop
    game_over = False
    reason = ""
    
    while not game_over:
        game_state = turn(game_state, game_phases)
        game_over, reason = is_game_over(game_state)
    
    return game_state, reason

def main():
    # Example configuration
    config = {
        'board_size': 5,
        'max_turns': 100,
        'num_players': 2,
        'end_criteria': {
            'type': 'elimination',
            'turn_limit': 100
        }
    }
    
    final_state, end_reason = run_game(config)
    print(f"Game Over! {end_reason}")

if __name__ == "__main__":
    main()

