import pytest
from actions.spawn_action import spawn_action
from game_state import GameState, Unit, Tile, Position, PlayerState, TurnState

def test_spawn_action_basic(initial_game_state):
    # Create a tile with one unit
    world = dict(initial_game_state.world)
    test_pos = (0, 2)
    unit = Unit(player_id=1, health=1, movement_points=1)
    world[test_pos] = Tile(position=test_pos, units=[unit])
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    state = GameState.from_state(initial_game_state, world=world, turns=turns)
    new_state = spawn_action(state, test_pos)
    
    # Check that a new unit was spawned
    assert len(new_state.world[test_pos].units) == 2
    assert all(u.player_id == 1 for u in new_state.world[test_pos].units)

def test_spawn_action_empty_tile(initial_game_state):
    # Test spawning on an empty tile
    test_pos = (0, 2)
    world = dict(initial_game_state.world)
    world[test_pos] = Tile(position=test_pos, units=[])
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    state = GameState.from_state(initial_game_state, world=world, turns=turns)
    new_state = spawn_action(state, test_pos)
    
    # Check that no spawn occurred
    assert len(new_state.world[test_pos].units) == 0

def test_spawn_action_multiple_players(initial_game_state):
    # Create a tile with units from different players
    world = dict(initial_game_state.world)
    test_pos = (0, 2)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=2, health=1, movement_points=1)
    ]
    world[test_pos] = Tile(position=test_pos, units=units)
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    state = GameState.from_state(initial_game_state, world=world, turns=turns)
    new_state = spawn_action(state, test_pos)
    
    # Check that no spawn occurred due to multiple players
    assert len(new_state.world[test_pos].units) == 2

def test_spawn_action_turn_recording(initial_game_state):
    # Test that spawn is recorded in turns dictionary
    world = dict(initial_game_state.world)
    test_pos = (0, 2)
    unit = Unit(player_id=1, health=1, movement_points=1)
    world[test_pos] = Tile(position=test_pos, units=[unit])
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    state = GameState.from_state(initial_game_state, world=world, turns=turns)
    new_state = spawn_action(state, test_pos)
    
    # Check turns dictionary was updated
    current_turn = new_state.current_turn
    turn_state = new_state.turns[current_turn]
    assert 'spawns' in turn_state.player_one.turn_model_output
    spawn_record = turn_state.player_one.turn_model_output['spawns'][0]
    assert spawn_record['position'] == test_pos
    assert spawn_record['player_id'] == 1

def test_spawn_action_multiple_existing_units(initial_game_state):
    # Test spawning with multiple existing units of same player
    world = dict(initial_game_state.world)
    test_pos = (0, 2)
    units = [
        Unit(player_id=1, health=1, movement_points=1),
        Unit(player_id=1, health=1, movement_points=1)
    ]
    world[test_pos] = Tile(position=test_pos, units=units)
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    state = GameState.from_state(initial_game_state, world=world, turns=turns)
    new_state = spawn_action(state, test_pos)
    
    # Check that spawn occurred
    assert len(new_state.world[test_pos].units) == 3
    assert all(u.player_id == 1 for u in new_state.world[test_pos].units)

def test_spawn_action_new_unit_properties(initial_game_state):
    # Test properties of spawned unit
    world = dict(initial_game_state.world)
    test_pos = (0, 2)
    unit = Unit(player_id=1, health=1, movement_points=1)
    world[test_pos] = Tile(position=test_pos, units=[unit])
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    state = GameState.from_state(initial_game_state, world=world, turns=turns)
    new_state = spawn_action(state, test_pos)
    
    # Check new unit properties
    new_unit = new_state.world[test_pos].units[-1]
    assert new_unit.player_id == 1
    assert new_unit.health == 1
    assert new_unit.movement_points == 1 