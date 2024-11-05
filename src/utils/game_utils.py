from typing import Dict, Any
from game_state import GameState

def print_game_state(state: GameState):
    print("\n\n" + "-" * 50)  # Add line break and dashed separator
    
    # Find the bounds of the world
    xs = [pos[0] for pos in state.world.keys()]
    ys = [pos[1] for pos in state.world.keys()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Print game status
    print(f"Turn: {state.current_turn - 1}/{state.max_turns - 1}")
    print(f"Game Status: {state.game_status}")
    
    
    # Print moves from current turn state
    print("\nMoves this turn:")
    print("-" * 40)
    print("p_id\tsrc\tdest\tunits")
    
    # need to get the previous turn state because ???
    current_turn_state = state.turns.get(state.current_turn - 1)
    if current_turn_state and current_turn_state.input_moves:
        for source_pos, players in current_turn_state.input_moves.items():
            for player_id, move_list in players.items():
                for move in move_list:
                    print(f"{player_id}\t{source_pos}\t{move['destination']}\t{move['units']}")
    else:
        print("No moves")
    
    # Print spawn information
    print("\nSpawns this turn:")
    print("-" * 40)
    print("p_id\tposition")
    
    if current_turn_state and current_turn_state.spawn_actions:
        for spawn in current_turn_state.spawn_actions:
            print(f"{spawn['player_id']}\t{spawn['position']}")
    else:
        print("No spawns")
    
    # Print combat results from player states
    print("\nCombats this turn:")
    print("-" * 40)
    print("pos\t\tp1_cas\tp2_cas")
    
    if current_turn_state:
        p1_combats = current_turn_state.player_one.turn_model_output.get('combats', [])
        p2_combats = current_turn_state.player_two.turn_model_output.get('combats', [])
        all_combats = p1_combats + p2_combats
        for combat in all_combats:
            print(f"{combat['position']}\t{combat.get('player_1_casualties', 0)}\t{combat.get('player_2_casualties', 0)}")
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
    pass