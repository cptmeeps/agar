from typing import Dict, Any
from game_types import GameState, Position, Tile, Unit

def create_sample_game_state() -> GameState:
    # Create a simple 5x5 world with some units
    world = {}
    for x in range(5):
        for y in range(5):
            pos = (x, y)
            units = []
            # Add player 1's unit at (0, 2) - left side
            if x == 0 and y == 2:
                units = [Unit(player_id=1, health=1, movement_points=1)]
            # Add player 2's unit at (4, 2) - right side
            elif x == 4 and y == 2:
                units = [Unit(player_id=2, health=1, movement_points=1)]
            
            world[pos] = Tile(Position(x, y), units)
    
    return GameState(
        world=world,
        current_turn=1,
        max_turns=10,
        num_players=2,
        game_status="in_progress",
        game_end_criteria={'type': 'elimination'},
        player_one_config={},
        player_two_config={},
        turns={},
        current_turn_input={}
    ) 

def print_game_state(state: GameState):
    print("\n" + "-" * 50)  # Add line break and dashed separator
    
    # Find the bounds of the world
    xs = [pos[0] for pos in state.world.keys()]
    ys = [pos[1] for pos in state.world.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Print game status
    print(f"Game Status: {state.game_status}")
    print(f"Turn: {state.current_turn}/{state.max_turns}")
    print("\nWorld Map:")
    
    # Print header
    print("    ", end="")
    for x in range(min_x, max_x + 1):
        print(f"|{x:^5}", end="")
    print("|")
    
    # Print separator line
    print("    " + "-" * ((max_x - min_x + 1) * 6 + 1))
    
    for y in range(min_y, max_y + 1):
        print(f"{y:2d}  ", end="")
        for x in range(min_x, max_x + 1):
            tile = state.world.get((x, y), None)
            counts = {1: 0, 2: 0}
            if tile and tile.units:
                for unit in tile.units:
                    counts[unit.player_id] = counts.get(unit.player_id, 0) + 1
            
            p1_display = '•' if counts[1] == 0 else str(counts[1])
            p2_display = '•' if counts[2] == 0 else str(counts[2])
            print(f"|{p1_display:>2} {p2_display:<2}", end="")
        print("|")
    
    # Print separator line
    print("    " + "-" * ((max_x - min_x + 1) * 6 + 1))
    print("     " + "P1 P2 " * (max_x - min_x + 1))
    print()

if __name__ == "__main__":
    game_state = create_sample_game_state()
    print_game_state(game_state) 