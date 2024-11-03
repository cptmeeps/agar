from typing import Dict, Tuple, Any
import yaml
from ..game_types import GameState
from ..llm import create_message_chain, call_llm_api, load_game_prompts
from ..utils import create_sample_game_state

def create_llm_world_representation(game_state: GameState, player_id: int) -> Dict[str, Any]:
    opponent_id = 2 if player_id == 1 else 1
    
    world_representation = {
        "game_info": {
            "current_turn": game_state.current_turn,
            "max_turns": game_state.max_turns,
            "game_status": game_state.game_status
        },
        "board": {
            "controlled_territories": {
                "your_territory": [],
                "enemy_territory": []
            },
            "hexes": []
        }
    }

    # Process each hex
    for pos, tile in game_state.world.items():
        q, r = pos
        
        # Group units by player
        units_count = {
            "your_units": 0,
            "enemy_units": 0
        }
        
        # Count units
        for unit in tile.units:
            if unit.player_id == player_id:
                units_count["your_units"] += 1
            else:
                units_count["enemy_units"] += 1

        # Determine hex control
        controlling_player = None
        if units_count["your_units"] > 0 and units_count["enemy_units"] == 0:
            controlling_player = "you"
            world_representation["board"]["controlled_territories"]["your_territory"].append(
                {"q": q, "r": r}
            )
        elif units_count["enemy_units"] > 0 and units_count["your_units"] == 0:
            controlling_player = "enemy"
            world_representation["board"]["controlled_territories"]["enemy_territory"].append(
                {"q": q, "r": r}
            )

        # Create hex representation
        hex_info = {
            "position": {"q": q, "r": r},
            "units": units_count,
            "controlled_by": controlling_player
        }
        world_representation["board"]["hexes"].append(hex_info)

    return world_representation

def create_strategic_prompt(game_state: GameState, player_id: int) -> Dict[str, Any]:
    # Get the world representation
    world_representation = create_llm_world_representation(game_state, player_id)
    
    # Load and prepare the prompt template
    prompt_template = load_game_prompts()
    game_state_yaml = yaml.dump(world_representation, sort_keys=False)
    
    return {
        'template': prompt_template,
        'variables': {'game_state_yaml': game_state_yaml}
    }

def get_ai_moves(game_state: GameState, player_id: int) -> Dict[str, Any]:
    # Create game state representation
    world_representation = create_llm_world_representation(game_state, player_id)
    game_state_yaml = yaml.dump(world_representation, sort_keys=False)
    
    # Create message chain with game state
    try:
        message_chain = create_message_chain(
            prompt_path="src/prompts/game_prompts.yaml",
            variables={'game_state_yaml': game_state_yaml}
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Error creating message chain: {e}")
        return {"moves": []}
    
    # Get and parse LLM response
    response = call_llm_api(message_chain)
    try:
        moves = yaml.safe_load(response)
        return moves
    except yaml.YAMLError:
        return {"moves": []}

def get_input_action(game_state: GameState, hex_pos: Tuple[int, int]) -> GameState:
    # Get moves from both AIs
    player_one_moves = get_ai_moves(game_state, 1)
    player_two_moves = get_ai_moves(game_state, 2)
    
    # Combine and restructure moves by source hex
    all_moves = {}
    for move in player_one_moves['moves'] + player_two_moves['moves']:
        source = tuple(move['source'])  # Convert [q, r] to (q, r)
        if source not in all_moves:
            all_moves[source] = []
        all_moves[source].append({
            'destination': tuple(move['destination']),
            'units': move['units']
        })
    
    # Update game state with restructured moves
    return GameState(
        **{**game_state.__dict__, 'current_turn_input': {'moves': all_moves}}
    ) 

def main():
    # Create sample game state
    game_state = create_sample_game_state()
    print("\n1. Created sample game state")
    
    # Test create_llm_world_representation
    world_rep = create_llm_world_representation(game_state, player_id=1)
    print("\n2. World representation for player 1:")
    print(yaml.dump(world_rep, sort_keys=False))
    
    # Test create_strategic_prompt
    prompt = create_strategic_prompt(game_state, player_id=1)
    print("\n3. Strategic prompt created:")
    print(yaml.dump(prompt, sort_keys=False))
    
    # Test get_ai_moves
    moves = get_ai_moves(game_state, player_id=1)
    print("\n4. AI moves generated:")
    print(yaml.dump(moves, sort_keys=False))
    
    # Test get_input_action
    updated_state = get_input_action(game_state, (0, 0))
    print("\n5. Final game state after input action:")
    print(f"Current turn input: {updated_state.current_turn_input}")

if __name__ == "__main__":
    main() 