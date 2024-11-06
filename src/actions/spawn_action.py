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
    
    # Get current turn state and create updated version
    current_turn = game_state.current_turn
    current_turn_state = game_state.turns[current_turn]
    
    # Create spawn record
    spawn_record = {
        'position': hex_pos,
        'player_id': player_id
    }
    
    # Create new turn state with updated world and spawn information
    new_turn_state = TurnState(
        turn_number=current_turn_state.turn_number,
        world=world,
        player_one=PlayerState(
            player_config=current_turn_state.player_one.player_config,
            turn_msg_chain=current_turn_state.player_one.turn_msg_chain,
            turn_model_output={
                **current_turn_state.player_one.turn_model_output,
                'spawns': [*current_turn_state.player_one.turn_model_output.get('spawns', []), spawn_record]
            },
            turn_input=current_turn_state.player_one.turn_input,
            turn_prompt_chain=current_turn_state.player_one.turn_prompt_chain,
            turn_prompt_config=current_turn_state.player_one.turn_prompt_config
        ),
        player_two=PlayerState(
            player_config=current_turn_state.player_two.player_config,
            turn_msg_chain=current_turn_state.player_two.turn_msg_chain,
            turn_model_output={
                **current_turn_state.player_two.turn_model_output,
                'spawns': [*current_turn_state.player_two.turn_model_output.get('spawns', []), spawn_record]
            },
            turn_input=current_turn_state.player_two.turn_input,
            turn_prompt_chain=current_turn_state.player_two.turn_prompt_chain,
            turn_prompt_config=current_turn_state.player_two.turn_prompt_config
        ),
        input_moves=current_turn_state.input_moves,
        move_actions=current_turn_state.move_actions,
        spawn_actions=[*current_turn_state.spawn_actions, spawn_record],
        combat_actions=current_turn_state.combat_actions
    )
    
    # Update turns dictionary
    turns = dict(game_state.turns)
    turns[current_turn] = new_turn_state
    
    spawn_event = GameEvent(
        type=GameEvent.Type.SPAWN,
        data={
            'position': hex_pos,
            'new_unit': new_unit,
            'turn_state': new_turn_state
        }
    )
    
    return game_state.apply_event(spawn_event) 