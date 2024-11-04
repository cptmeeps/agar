import yaml
from typing import Dict, Any
from game_types import GameState, Position, Tile, Unit

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
    
    # Print moves from turns dictionary
    print("\nMoves this turn:")
    print("-" * 40)
    print("p_id\tsrc\tdest\tunits")
    
    # Get current turn's moves from turns dictionary
    turn_data = state.turns.get(state.current_turn -1, {})
    turn_input = turn_data.get('turn_input', {})
    if 'moves' in turn_input:
        moves = turn_input['moves']
        for source_pos, players in moves.items():
            for player_id, move_list in players.items():
                for move in move_list:
                    print(f"{player_id}\t{source_pos}\t{move['destination']}\t{move['units']}")
    else:
        print("No moves")
    
    # Print spawns from turns dictionary
    print("\nSpawns this turn:")
    print("-" * 40)
    print("p_id\thex")
    
    if 'spawns' in turn_data:
        spawns = turn_data['spawns']
        for spawn in spawns:
            print(f"{spawn['player']}\t{spawn['hex']}")
    else:
        print("No spawns")
    
    # Print combat results from turns dictionary
    print("\nCombats this turn:")
    print("-" * 40)
    print("pos\t\tp1_cas\tp2_cas")
    
    if 'combats' in turn_data:
        combats = turn_data['combats']
        for combat in combats:
            print(f"{combat['position']}\t{combat['player_1_casualties']}\t{combat['player_2_casualties']}")
    else:
        print("No combats")
    
    # Print the world
    print("\nWorld:")
    print("-" * 40)  
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