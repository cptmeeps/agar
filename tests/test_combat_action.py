import pytest
from combat_action import combat_action
from game_state import GameState, Unit, Tile, Position, TurnState, PlayerState
import random

@pytest.fixture
def mock_random_roll(monkeypatch):
    def mock_randint(a, b):
        return 7  # Always return 7 for predictable combat results
    monkeypatch.setattr(random, "randint", mock_randint)

def test_combat_action_no_combat(initial_game_state):
    # Test when there's only one unit on the tile
    state = GameState.from_state(initial_game_state)
    new_state = combat_action(state, (0, 2))
    
    # State should remain unchanged
    assert len(new_state.world[(0, 2)].units) == len(state.world[(0, 2)].units)

def test_combat_action_same_player(initial_game_state):
    # Test when all units belong to the same player
    world = dict(initial_game_state.world)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=1, health=1, movement_points=1)
    ]
    world[(0, 2)] = Tile(position=Position(0, 2), units=units)
    
    state = GameState.from_state(initial_game_state, world=world)
    new_state = combat_action(state, (0, 2))
    
    # State should remain unchanged
    assert len(new_state.world[(0, 2)].units) == 2

def test_combat_action_basic_combat(initial_game_state, mock_random_roll):
    # Test basic combat between two players
    world = dict(initial_game_state.world)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=2, health=1, movement_points=1)
    ]
    world[(0, 2)] = Tile(position=Position(0, 2), units=units)
    
    state = GameState.from_state(initial_game_state, world=world)
    new_state = combat_action(state, (0, 2))
    
    # With mock roll of 7, both players succeed and eliminate each other
    assert len(new_state.world[(0, 2)].units) == 0
    
    # Check combat was recorded in turns
    turn_state = new_state.turns[state.current_turn]
    assert 'combats' in turn_state.player_one.turn_model_output
    combat_record = turn_state.player_one.turn_model_output['combats'][0]
    assert combat_record['position'] == (0, 2)
    assert combat_record['player_1_casualties'] == 1
    assert combat_record['player_2_casualties'] == 1

def test_combat_action_multiple_units(initial_game_state, mock_random_roll):
    # Test combat with multiple units per player
    world = dict(initial_game_state.world)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=2, health=1, movement_points=1),
        Unit(player_id=2, health=1, movement_points=1)
    ]
    world[(0, 2)] = Tile(position=Position(0, 2), units=units)
    
    state = GameState.from_state(initial_game_state, world=world)
    new_state = combat_action(state, (0, 2))
    
    # With mock roll of 7, both players succeed and deal 2 damage each
    assert len(new_state.world[(0, 2)].units) == 0

def test_combat_action_uneven_forces(initial_game_state, mock_random_roll):
    # Test combat with uneven forces
    world = dict(initial_game_state.world)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=2, health=1, movement_points=1)
    ]
    world[(0, 2)] = Tile(position=Position(0, 2), units=units)
    
    state = GameState.from_state(initial_game_state, world=world)
    new_state = combat_action(state, (0, 2))
    
    # Player 1 deals 2 damage, Player 2 deals 1 damage
    assert len(new_state.world[(0, 2)].units) == 1
    assert new_state.world[(0, 2)].units[0].player_id == 1

def test_combat_action_failed_roll(initial_game_state):
    # Test combat with failed roll
    def mock_failed_roll(a, b):
        return 3  # Always fail with 3
    
    world = dict(initial_game_state.world)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=2, health=1, movement_points=1)
    ]
    world[(0, 2)] = Tile(position=Position(0, 2), units=units)
    
    with pytest.MonkeyPatch().context() as m:
        m.setattr(random, "randint", mock_failed_roll)
        state = GameState.from_state(initial_game_state, world=world)
        new_state = combat_action(state, (0, 2))
        
        # Both rolls fail, no casualties
        assert len(new_state.world[(0, 2)].units) == 2 