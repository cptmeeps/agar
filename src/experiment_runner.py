import yaml
from pathlib import Path
from typing import Dict, Any, List
from game_state import GameState
from engine import run_game
import shutil
from itertools import combinations

def load_experiment_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_experiment_environment(experiment_config: Dict[str, Any]) -> Path:
    experiment_name = experiment_config['experiment_name']
    results_dir = Path('results') / experiment_name
    results_dir.mkdir(parents=True, exist_ok=True)

    # Copy necessary prompt templates
    prompts_to_copy = get_prompts_from_config(experiment_config)
    copy_prompts(prompts_to_copy, results_dir / 'prompts')

    return results_dir

def get_prompts_from_config(experiment_config: Dict[str, Any]) -> set:
    """
    Collects all unique prompt file paths from the player configurations.
    """
    prompts_set = set()
    player_configs = experiment_config.get('player_configs', [])
    for player_config in player_configs:
        prompt_chain = player_config.get('turn_prompt_config', [])
        for prompt in prompt_chain:
            prompts_set.add(prompt['prompt_filepath'])
    return prompts_set

def copy_prompts(prompt_files: set, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    for prompt_file in prompt_files:
        src = Path('src/prompts') / prompt_file
        dst = destination / prompt_file
        shutil.copy(src, dst)

def run_experiment(experiment_config: Dict[str, Any], results_dir: Path) -> List[GameState]:
    iterations = experiment_config.get('iterations', 1)
    player_configs = experiment_config.get('player_configs', [])
    experiment_results = []

    # Generate all possible pairs of player configurations
    player_pairs = list(combinations(player_configs, 2))

    for i in range(iterations):
        print(f"Running iteration {i+1}/{iterations}")
        for pair_idx, (player_one_config, player_two_config) in enumerate(player_pairs, start=1):
            print(f"\nRunning game {pair_idx} between {player_one_config.get('name')} and {player_two_config.get('name')}")
            # Create initial game state with the experiment's configurations
            initial_state = GameState.from_config({
                'board_size': 5,
                'max_turns': 10,
                'num_players': 2,
                'end_criteria': {'type': 'elimination'},
                'player_one_config': player_one_config,
                'player_two_config': player_two_config,
            })
            # Run the game
            final_state = run_game(initial_state)
            # Save the result
            save_game_result(final_state, results_dir, iteration=i+1, game_num=pair_idx)
            # Collect results for analysis
            experiment_results.append(final_state)
    return experiment_results

def save_game_result(game_state: GameState, results_dir: Path, iteration: int, game_num: int):
    """
    Saves the final game result for each game in an iteration.
    """
    iteration_dir = results_dir / f'iteration_{iteration}' / f'game_{game_num}'
    iteration_dir.mkdir(parents=True, exist_ok=True)
    result_data = {
        'final_scores': game_state.scores,
        'player_one_config': game_state.player_one_config,
        'player_two_config': game_state.player_two_config,
    }
    game_state_path = iteration_dir / 'final_results.yaml'
    with open(game_state_path, 'w') as f:
        yaml.dump(result_data, f)

def main():
    print("\n" * 5)
    print("\n" + "="*80)
    print("1. Testing load_experiment_config")
    print("Expected: Load experiment configuration from a YAML file")
    print("="*80)
    
    # Since we cannot read from a file in this test, simulate loading a configuration
    test_experiment_config = {
        'experiment_name': 'test_experiment',
        'iterations': 2,
        'player_configs': [
            {
                'name': 'Player_A',
                'turn_prompt_config': [
                    {
                        'prompt_filepath': 'expansion.txt',
                        'template_params': {}
                    }
                ]
            },
            {
                'name': 'Player_B',
                'turn_prompt_config': [
                    {
                        'prompt_filepath': 'attack.txt',
                        'template_params': {}
                    }
                ]
            },
            # {
            #     'name': 'Player_C',
            #     'turn_prompt_config': [
            #         {
            #             'prompt_filepath': 'defend.txt',
            #             'template_params': {}
            #         }
            #     ]
            # }
        ]
    }
    print("Loaded experiment configuration:")
    print(yaml.dump(test_experiment_config))

    print("\n" + "="*80)
    print("2. Testing setup_experiment_environment")
    print("Expected: Creates results directory and copies prompt files")
    print("="*80)

    # Normally this would create directories and copy files, but for testing we'll simulate it
    try:
        results_dir = setup_experiment_environment(test_experiment_config)
        print(f"Results directory set up at: {results_dir}")
    except Exception as e:
        print(f"Error setting up experiment environment: {e}")

    print("\n" + "="*80)
    print("3. Testing get_prompts_from_config")
    print("Expected: Extracts prompt file paths from all player configurations")
    print("="*80)
    prompts = get_prompts_from_config(test_experiment_config)
    print("Prompts to copy:")
    print(prompts)

    print("\n" + "="*80)
    print("4. Testing run_experiment")
    print("Expected: Runs the experiment for all player pairs over specified iterations")
    print("="*80)
    # Simulate running the experiment
    try:
        experiment_results = run_experiment(test_experiment_config, results_dir)
        print(f"Experiment completed with {len(experiment_results)} games.")
    except Exception as e:
        print(f"Error running experiment: {e}")

    print("\n" + "="*80)
    print("5. Testing save_game_result")
    print("Expected: Game results are saved for each pair in each iteration")
    print("="*80)
    # Since `save_game_result` is called within `run_experiment`, we assume it works
    # Verify that the game results have been collected
    for idx, game_state in enumerate(experiment_results, start=1):
        print(f"Game {idx}: Final Scores - {game_state.scores}")

if __name__ == "__main__":
    main() 