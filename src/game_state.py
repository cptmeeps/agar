from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from game_types import Position, Unit, Tile

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

    def is_valid_state_change(self, new_state: 'GameState', phase: str | None = None) -> bool:
        """
        Validates if the state change is legal for the given game phase.
        
        Args:
            new_state: The proposed new GameState
            phase: Current game phase ('input', 'move', 'combat', 'spawn', 'turn_end'). 
                  If None, validates general state changes.
            
        Returns:
            bool: True if the state change is valid, False otherwise
        """
        # TODO: Implement validation logic for each phase
        # For now, always return True
        return True

def create_sample_game_state() -> GameState:
    # Create a simple 5x5 world with some units
    world = {}
    for x in range(5):
        for y in range(5):
            pos = (x, y)
            units = []
            # Add player 1's units at (0, 2) - left side
            if x == 0 and y == 2:
                units = [
                    Unit(player_id=1, health=1, movement_points=1),
                    Unit(player_id=1, health=1, movement_points=1)
                ]
            # Add player 2's units at (4, 2) - right side
            elif x == 4 and y == 2:
                units = [
                    Unit(player_id=2, health=1, movement_points=1),
                    Unit(player_id=2, health=1, movement_points=1)
                ]
            
            world[pos] = Tile(Position(x, y), units)
    
    return GameState(
        world=world,
        current_turn=0,
        max_turns=10,
        num_players=2,
        game_status="in_progress",
        game_end_criteria={'type': 'elimination'},
        player_one_config={},
        player_two_config={},
        turns={}
    ) 