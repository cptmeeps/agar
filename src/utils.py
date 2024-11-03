from typing import Dict, Any
from .game_types import GameState, Position, Tile, Unit

def create_sample_game_state() -> GameState:
    # Create a simple 3x3 world with some units
    world = {}
    for q in range(-1, 2):
        for r in range(-1, 2):
            pos = (q, r)
            units = []
            # Add some sample units
            if q == 0 and r == 0:
                units = [
                    Unit(player_id=1, health=1, movement_points=1),
                    Unit(player_id=1, health=1, movement_points=1)
                ]
            elif q == 1 and r == 0:
                units = [Unit(player_id=2, health=1, movement_points=1)]
            
            world[pos] = Tile(Position(q, r), units)
    
    return GameState(
        world=world,
        current_turn=1,
        max_turns=100,
        num_players=2,
        game_status="in_progress",
        game_end_criteria={'type': 'elimination'},
        player_one_config={},
        player_two_config={},
        turns={},
        current_turn_input={}
    ) 