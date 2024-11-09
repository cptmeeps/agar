import yaml
from pathlib import Path
from typing import Dict, Any, List
from game_state import GameState
from engine import run_game
from itertools import combinations

def load_experiment_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        experiment_config = yaml.safe_load(f)
    
    # Load player configurations from specified files
    player_config_files = experiment_config.get('player_config_files', [])
    player_configs = []
    for pc_file in player_config_files:
        with open(pc_file, 'r') as pc_f:
            pc_data = yaml.safe_load(pc_f)
            # Assume each player config file contains a list of player configs
            player_configs.extend(pc_data.get('player_configs', []))
    
    experiment_config['player_configs'] = player_configs
    return experiment_config

def setup_experiment_environment(experiment_config: Dict[str, Any]) -> Path:
    experiment_name = experiment_config['experiment_name']
    results_dir = Path('results') / experiment_name
    results_dir.mkdir(parents=True, exist_ok=True)

    return results_dir

def run_experiment(experiment_config: Dict[str, Any], results_dir: Path) -> List[GameState]:
    iterations = experiment_config.get('iterations', 1)
    player_configs = experiment_config.get('player_configs', [])
    experiment_results = []

    # Generate all possible pairs of player configurations
    player_pairs = list(combinations(player_configs, 2))

    for pair_idx, (player_one_config, player_two_config) in enumerate(player_pairs, start=1):
        player_one_name = player_one_config.get('name', f"Player_{pair_idx}_1")
        player_two_name = player_two_config.get('name', f"Player_{pair_idx}_2")
        print(f"\nRunning games between {player_one_name} and {player_two_name}")
        matchup_results = []
        for i in range(iterations):
            print(f"Running iteration {i+1}/{iterations}")
            # Create initial game state with the experiment's configurations
            initial_state = GameState.from_config({
                'board_size': 5,
                'max_turns': 5,
                'num_players': 2,
                'end_criteria': {'type': 'elimination'},
                'player_one_config': player_one_config,
                'player_two_config': player_two_config,
            })
            # Run the game
            final_state = run_game(initial_state)
            # Collect results
            matchup_results.append({
                'iteration': i + 1,
                'final_scores': final_state.scores,
                'player_one_name': player_one_name,
                'player_two_name': player_two_name,
            })
            experiment_results.append(final_state)
        # Save the results for this matchup
        save_game_result(matchup_results, results_dir, player_one_name, player_two_name)
    return experiment_results

def save_game_result(matchup_results: List[Dict], results_dir: Path, player_one_name: str, player_two_name: str):
    """
    Saves the final game results for each matchup.
    """
    matchup_filename = f"{player_one_name}_vs_{player_two_name}.yaml"
    matchup_path = results_dir / matchup_filename

    with open(matchup_path, 'w') as f:
        yaml.dump(matchup_results, f)

def save_experiment_results(experiment_results: List[GameState], results_dir: Path):
    """
    Saves the overall experiment results to a file.
    """
    experiment_results_data = []

    for idx, game_state in enumerate(experiment_results, start=1):
        experiment_results_data.append({
            'game_number': idx,
            'final_scores': game_state.scores,
            'player_one_name': game_state.player_one_config.get('name'),
            'player_two_name': game_state.player_two_config.get('name'),
        })

    experiment_results_path = results_dir / 'experiment_results.yaml'

    with open(experiment_results_path, 'w') as f:
        yaml.dump(experiment_results_data, f)

def main():
    # Load experiment configuration from a file
    print("\n" * 5)
    print("\n"+ "\n" + "=" * 60)
    print("Loading experiment configuration")
    experiment_config_path = 'configs/experiments/test_experiment.yaml'
    experiment_config = load_experiment_config(experiment_config_path)
    print(f"Experiment '{experiment_config.get('experiment_name')}' loaded.")
    print(f"Player configurations loaded: {[pc.get('name') for pc in experiment_config['player_configs']]}")

    # Set up the experiment environment
    print("\n"+ "\n" + "=" * 60)
    print("Setting up experiment environment")
    try:
        results_dir = setup_experiment_environment(experiment_config)
        print(f"Results directory set up at: {results_dir}")
    except Exception as e:
        print(f"Error setting up experiment environment: {e}")

    # Run the experiment
    print("\n"+ "\n" + "=" * 60)
    print("Running experiment")
    try:
        experiment_results = run_experiment(experiment_config, results_dir)
        print(f"Experiment completed with {len(experiment_results)} games.")

        # Save the overall experiment results
        save_experiment_results(experiment_results, results_dir)

    except Exception as e:
        print(f"Error running experiment: {e}")

    # Verify that the game results have been collected
    for idx, game_state in enumerate(experiment_results, start=1):
        print(f"Game {idx}: Final Scores - {game_state.scores}")

if __name__ == "__main__":
    main() 