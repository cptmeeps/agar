import pytest
from input_action import (
    create_llm_world_representation,
    get_ai_moves,
    get_input_action
)
from game_state import GameState, Unit, Tile, Position, TurnState, PlayerState
from unittest.mock import patch, MagicMock

@pytest.fixture
def sample_game_state(initial_game_state):
    # Modify initial game state to have some units
    world = dict(initial_game_state.world)
    
    # Add player 1 units at (0,0)
    world[(0, 0)] = Tile(
        position=Position(0, 0),
        units=[
            Unit(player_id=1, health=1, movement_points=1),
            Unit(player_id=1, health=1, movement_points=1)
        ]
    )
    
    # Add player 2 units at (2,2)
    world[(2, 2)] = Tile(
        position=Position(2, 2),
        units=[Unit(player_id=2, health=1, movement_points=1)]
    )
    
    # Add mixed units at (1,1)
    world[(1, 1)] = Tile(
        position=Position(1, 1),
        units=[
            Unit(player_id=1, health=1, movement_points=1),
            Unit(player_id=2, health=1, movement_points=1)
        ]
    )
    
    # Create proper turn state
    turns = {
        1: TurnState(
            turn_number=1,
            world=world,
            player_one=PlayerState(),
            player_two=PlayerState()
        )
    }
    
    return GameState(**{
        **initial_game_state.__dict__, 
        'world': world,
        'turns': turns
    })

def test_create_llm_world_representation_basic(sample_game_state):
    world_rep = create_llm_world_representation(sample_game_state, player_id=1)
    
    assert "game_info" in world_rep
    assert "board" in world_rep
    assert "cells" in world_rep["board"]
    assert "controlled_territories" in world_rep["board"]

def test_create_llm_world_representation_unit_counts(sample_game_state):
    world_rep = create_llm_world_representation(sample_game_state, player_id=1)
    
    # Check (0,0) - player 1 territory
    assert world_rep["board"]["cells"]["0,0"]["units"]["your_units"] == 2
    assert world_rep["board"]["cells"]["0,0"]["units"]["enemy_units"] == 0
    assert world_rep["board"]["cells"]["0,0"]["controlled_by"] == "you"
    
    # Check (2,2) - player 2 territory
    assert world_rep["board"]["cells"]["2,2"]["units"]["your_units"] == 0
    assert world_rep["board"]["cells"]["2,2"]["units"]["enemy_units"] == 1
    assert world_rep["board"]["cells"]["2,2"]["controlled_by"] == "enemy"
    
    # Check (1,1) - contested territory
    assert world_rep["board"]["cells"]["1,1"]["units"]["your_units"] == 1
    assert world_rep["board"]["cells"]["1,1"]["units"]["enemy_units"] == 1
    assert world_rep["board"]["cells"]["1,1"]["controlled_by"] is None

def test_create_llm_world_representation_territories(sample_game_state):
    world_rep = create_llm_world_representation(sample_game_state, player_id=1)
    
    your_territory = world_rep["board"]["controlled_territories"]["your_territory"]
    enemy_territory = world_rep["board"]["controlled_territories"]["enemy_territory"]
    
    assert {"x": 0, "y": 0} in your_territory
    assert {"x": 2, "y": 2} in enemy_territory

@patch('input_action.call_llm_api')
@patch('input_action.create_message_chain')
def test_get_ai_moves_success(mock_create_chain, mock_call_api, sample_game_state):
    mock_create_chain.return_value = ["test chain"]
    mock_call_api.return_value = '{"moves": [{"source": [0, 0], "destination": [1, 0], "units": 1}]}'
    
    result = get_ai_moves(sample_game_state, player_id=1)
    
    assert "moves" in result
    assert len(result["moves"]) == 1
    assert result["moves"][0]["source"] == [0, 0]

@patch('input_action.call_llm_api')
@patch('input_action.create_message_chain')
def test_get_ai_moves_invalid_response(mock_create_chain, mock_call_api, sample_game_state):
    mock_create_chain.return_value = ["test chain"]
    mock_call_api.return_value = 'invalid json'
    
    result = get_ai_moves(sample_game_state, player_id=1)
    
    assert result == {}
