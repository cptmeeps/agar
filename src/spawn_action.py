from typing import Dict, Tuple, Any
from game_state import GameState, Tile, Unit, PlayerState, TurnState, SpawnStateChange
from utils.logger import logger
from game_state import GameEvent
import json

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
    
    # Only spawn if one player controls the hex and has at least one unit
    if len(players_units) != 1:
        return game_state
        
    # print("players_units at", hex_pos, ":", players_units)
    player_id = list(players_units.keys())[0]
    if len(players_units[player_id]) < 1:
        return game_state
    # print(f"Turn {game_state.current_turn}: Spawning unit for player {player_id} at {hex_pos}")

    # Create new unit
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
    
    # Log spawn event
    logger.log_action(
        "spawn",
        game_state,
        position=hex_pos,
        details={"player_id": player_id}
    )
    
    # Create spawn record
    spawn_record = {
        'position': hex_pos,
        'player_id': player_id
    }
    
    # Update turn state
    turns = dict(game_state.turns)
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]
    
    # Update player states using from_state
    new_player_one = PlayerState.from_state(
        current_turn_state.player_one,
        turn_model_output={
            **current_turn_state.player_one.turn_model_output,
            'spawns': [*current_turn_state.player_one.turn_model_output.get('spawns', []), spawn_record]
        }
    )

    new_player_two = PlayerState.from_state(
        current_turn_state.player_two,
        turn_model_output={
            **current_turn_state.player_two.turn_model_output,
            'spawns': [*current_turn_state.player_two.turn_model_output.get('spawns', []), spawn_record]
        }
    )

    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=world,
        player_one=new_player_one,
        player_two=new_player_two,
        spawn_actions=[*current_turn_state.spawn_actions, spawn_record]
    )
    
    turns[current_turn] = new_turn_state
    
    return (GameState.builder(game_state)
            .with_world(world)
            .with_turns(turns)
            .build()) 

def main():
    # Create a test configuration (same as input_action.py)
    test_config = {
        'board_size': 5,
        'max_turns': 10,
        'num_players': 2,
        'player_one_config': {
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        },
        'player_two_config': {
            'turn_prompt_config': [{
                'prompt_filepath': 'test_prompts.txt',
                'template_params': {}
            }]
        }
    }

    # Create initial game state
    game_state = GameState.from_config(test_config)

    print("\n" + "="*80)
    print("1. Testing spawn_action with default starting position")
    print("Expected: New unit should spawn at (0,2) for Player 1")
    print("="*80)
    
    # Print initial state
    initial_pos = (0, 2)
    initial_tile = game_state.world[initial_pos]
    print(f"\nInitial units at {initial_pos}:")
    for unit in initial_tile.units:
        print(f"Player {unit.player_id} unit - Health: {unit.health}, Movement: {unit.movement_points}")

    # Test spawn action
    try:
        new_state = spawn_action(game_state, initial_pos)
        new_tile = new_state.world[initial_pos]
        
        print(f"\nUnits after spawn at {initial_pos}:")
        for unit in new_tile.units:
            print(f"Player {unit.player_id} unit - Health: {unit.health}, Movement: {unit.movement_points}")
        
        # Check spawn records
        current_turn = new_state.turns[new_state.current_turn]
        print("\nSpawn records in turn state:")
        print(json.dumps(current_turn.spawn_actions, indent=2))
        
    except Exception as e:
        print(f"❌ Error in spawn action: {str(e)}")

    print("\n" + "="*80)
    print("2. Testing spawn_action with contested position")
    print("Expected: No spawn should occur when multiple players present")
    print("="*80)

    # Create a contested position
    contested_pos = (2, 2)
    contested_tile = Tile(
        position=contested_pos,
        units=[
            Unit(player_id=1, health=1, movement_points=1),
            Unit(player_id=2, health=1, movement_points=1)
        ]
    )
    
    # Update world with contested position
    test_world = dict(game_state.world)
    test_world[contested_pos] = contested_tile
    test_state = GameState.builder(game_state).with_world(test_world).build()

    print(f"\nInitial units at contested position {contested_pos}:")
    for unit in contested_tile.units:
        print(f"Player {unit.player_id} unit - Health: {unit.health}, Movement: {unit.movement_points}")

    try:
        new_state = spawn_action(test_state, contested_pos)
        new_tile = new_state.world[contested_pos]
        
        print(f"\nUnits after attempted spawn at {contested_pos}:")
        for unit in new_tile.units:
            print(f"Player {unit.player_id} unit - Health: {unit.health}, Movement: {unit.movement_points}")
            
    except Exception as e:
        print(f"❌ Error in spawn action: {str(e)}")

if __name__ == "__main__":
    main() 