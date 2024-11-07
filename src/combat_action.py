from typing import Dict, Tuple, Any
import random
from game_state import GameState, Tile, PlayerState, TurnState, Unit
from utils.logger import logger
import json

def combat_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    tile = game_state.world[hex_pos]
    if len(tile.units) <= 1:
        return game_state
    
    players_units = {}
    for unit in tile.units:
        if unit.player_id not in players_units:
            players_units[unit.player_id] = []
        players_units[unit.player_id].append(unit)
    
    if len(players_units) <= 1:
        return game_state
    
    initial_counts = {player_id: len(units) for player_id, units in players_units.items()}
    damage_dealt = {player_id: 0 for player_id in players_units.keys()}
    
    # Combat rolls - each player rolls once
    for player_id in players_units.keys():
        roll = random.randint(1, 10)
        if roll > 4:  # Success on 5 or higher (60% chance)
            # Calculate damage based on initial unit count
            for other_player_id in players_units.keys():
                if other_player_id != player_id:
                    damage_dealt[other_player_id] += initial_counts[player_id]
    
    # Apply damage to all players
    surviving_units = []
    for player_id, units in players_units.items():
        # Keep only surviving units
        survivors = units[damage_dealt[player_id]:]
        surviving_units.extend(survivors)
    
    # Update the world with surviving units
    world = dict(game_state.world)
    world[hex_pos] = Tile(
        position=tile.position,
        units=surviving_units
    )
    
    # Create combat record
    combat_record = {
        'position': hex_pos,
        'player_1_casualties': min(damage_dealt.get(1, 0), initial_counts.get(1, 0)),
        'player_2_casualties': min(damage_dealt.get(2, 0), initial_counts.get(2, 0))
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
            'combats': [*current_turn_state.player_one.turn_model_output.get('combats', []), combat_record]
        }
    )

    new_player_two = PlayerState.from_state(
        current_turn_state.player_two,
        turn_model_output={
            **current_turn_state.player_two.turn_model_output,
            'combats': [*current_turn_state.player_two.turn_model_output.get('combats', []), combat_record]
        }
    )

    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=world,
        player_one=new_player_one,
        player_two=new_player_two,
        combat_actions=[*current_turn_state.combat_actions, combat_record]
    )
    
    turns[current_turn] = new_turn_state
    
    # Use builder to create new state
    return (GameState.builder(game_state)
            .with_world(world)
            .with_turns(turns)
            .build())
    
    # Log combat results
    logger.log_combat(
        game_state,
        hex_pos,
        damage_dealt
    )
    
    return GameState.from_state(game_state, world=world, turns=turns) 

def main():
    # Create a test configuration similar to input_action
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
    
    # Test position where combat will occur
    combat_pos = (2, 2)
    
    print("\n" + "="*40)
    print("1. Testing Combat Setup")
    print("Expected: A tile with units from multiple players")
    print("="*80)
    
    # Manually add units from different players to create a combat scenario
    world = dict(game_state.world)
    test_tile = Tile(
        position=combat_pos,
        units=[
            Unit(player_id=1, health=1, movement_points=1),  # Add 3 units for player 1
            Unit(player_id=1, health=1, movement_points=1),
            Unit(player_id=1, health=1, movement_points=1),
            Unit(player_id=2, health=1, movement_points=1),  # Add 2 units for player 2
            Unit(player_id=2, health=1, movement_points=1),
        ]
    )
    world[combat_pos] = test_tile
    
    # Create new game state with our test setup
    game_state = GameState.builder(game_state).with_world(world).build()
    
    print(f"\nInitial state at position {combat_pos}:")
    print(f"Player 1 units: {sum(1 for unit in test_tile.units if unit.player_id == 1)}")
    print(f"Player 2 units: {sum(1 for unit in test_tile.units if unit.player_id == 2)}")

    print("\n" + "="*80)
    print("2. Testing Combat Resolution")
    print("Expected: Combat results showing casualties and survivors")
    print("="*80)
    
    try:
        # Execute combat
        new_state = combat_action(game_state, combat_pos)
        
        # Get the resulting tile
        result_tile = new_state.world[combat_pos]
        
        print("\nCombat Results:")
        print(f"Surviving Player 1 units: {sum(1 for unit in result_tile.units if unit.player_id == 1)}")
        print(f"Surviving Player 2 units: {sum(1 for unit in result_tile.units if unit.player_id == 2)}")
        
        # Print combat records
        current_turn = new_state.turns[new_state.current_turn]
        print("\nCombat Records:")
        print(json.dumps(current_turn.combat_actions, indent=2))
        
    except Exception as e:
        print(f"❌ Error in combat resolution: {str(e)}")

if __name__ == "__main__":
    main() 