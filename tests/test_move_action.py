import pytest
from move_action import move_action
from game_state import GameState, Unit, Tile, Position, TurnState, PlayerState

def test_move_action_basic(initial_game_state):
    # Create a move in input_moves
    turns = {
        1: TurnState(
            turn_number=1,
            world=initial_game_state.world,
            player_one=PlayerState(),
            player_two=PlayerState(),
            input_moves={(0, 2): {1: [{'destination': (1, 2), 'units': 1}]}}
        )
    }
    
    state = GameState.from_state(initial_game_state, turns=turns)
    new_state = move_action(state, (0, 2))
    
    # Check source tile has one unit remaining
    assert len(new_state.world[(0, 2)].units) == 1
    
    # Check destination tile has one unit
    assert len(new_state.world[(1, 2)].units) == 1
    assert new_state.world[(1, 2)].units[0].player_id == 1

def test_move_action_invalid_destination(initial_game_state):
    turns = {
        1: TurnState(
            turn_number=1,
            world=initial_game_state.world,
            player_one=PlayerState(),
            player_two=PlayerState(),
            input_moves={(0, 2): {1: [{'destination': (10, 10), 'units': 1}]}}
        )
    }
    
    state = GameState.from_state(initial_game_state, turns=turns)
    new_state = move_action(state, (0, 2))
    
    # State should remain unchanged
    assert len(new_state.world[(0, 2)].units) == 2
    assert (10, 10) not in new_state.world

def test_move_action_too_many_units(initial_game_state):
    turns = {
        1: TurnState(
            turn_number=1,
            world=initial_game_state.world,
            player_one=PlayerState(),
            player_two=PlayerState(),
            input_moves={(0, 2): {1: [{'destination': (1, 2), 'units': 5}]}}
        )
    }
    
    state = GameState.from_state(initial_game_state, turns=turns)
    new_state = move_action(state, (0, 2))
    
    # State should remain unchanged
    assert len(new_state.world[(0, 2)].units) == 2
    assert len(new_state.world[(1, 2)].units) == 0

def test_move_action_multiple_moves(initial_game_state):
    turns = {
        1: TurnState(
            turn_number=1,
            world=initial_game_state.world,
            player_one=PlayerState(),
            player_two=PlayerState(),
            input_moves={(0, 2): {1: [
                {'destination': (1, 2), 'units': 1},
                {'destination': (1, 1), 'units': 1}
            ]}}
        )
    }
    
    state = GameState.from_state(initial_game_state, turns=turns)
    new_state = move_action(state, (0, 2))
    
    assert len(new_state.world[(0, 2)].units) == 0
    assert len(new_state.world[(1, 2)].units) == 1
    assert len(new_state.world[(1, 1)].units) == 1

def test_move_action_to_occupied_tile(initial_game_state):
    # First add a unit to the destination tile
    world = dict(initial_game_state.world)
    dest_tile = world[(1, 2)]
    existing_unit = Unit(player_id=1, health=1, movement_points=1)
    world[(1, 2)] = Tile(position=dest_tile.position, units=[existing_unit])
    
    state = GameState(**{**initial_game_state.__dict__, 'world': world})
    
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState(),
            input_moves={(0, 2): {1: [{'destination': (1, 2), 'units': 1}]}}
        )
    }
    
    state = GameState.from_state(state, turns=turns)
    new_state = move_action(state, (0, 2))
    
    assert len(new_state.world[(0, 2)].units) == 1
    assert len(new_state.world[(1, 2)].units) == 2

def test_move_action_no_moves(initial_game_state):
    turns = {
        1: TurnState(
            turn_number=1,
            world=initial_game_state.world,
            player_one=PlayerState(),
            player_two=PlayerState(),
            input_moves={}
        )
    }
    
    state = GameState.from_state(initial_game_state, turns=turns)
    new_state = move_action(state, (0, 2))
    
    # State should remain unchanged
    assert len(new_state.world[(0, 2)].units) == 2