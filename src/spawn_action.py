from typing import Dict, Tuple, Any
from game_state import GameState, Tile, Unit, PlayerState, TurnState, SpawnStateChange
from utils.logger import logger
from game_state import GameEvent

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