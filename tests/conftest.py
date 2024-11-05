import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from game_state import GameState

@pytest.fixture
def basic_config():
    return {
        'board_size': 5,
        'max_turns': 10,
        'num_players': 2,
        'end_criteria': {'type': 'elimination'},
        'player_one_config': {},
        'player_two_config': {}
    }

@pytest.fixture
def initial_game_state(basic_config):
    return GameState.from_config(basic_config)
