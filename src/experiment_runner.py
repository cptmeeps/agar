import yaml
from pathlib import Path
from typing import Dict, Any, List
from game_state import GameState
from engine import run_game
import shutil

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
    prompts_set = set()
    for player_config_key in ['player_one_config', 'player_two_config']:
        player_config = experiment_config.get(player_config_key, {})
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
    experiment_results = []
    for i in range(iterations):
        print(f"Running iteration {i+1}/{iterations}")
        # Create initial game state with the experiment's configurations
        initial_state = GameState.from_config({
            'board_size': 5,
            'max_turns': 10,
            'num_players': 2,
            'end_criteria': {'type': 'elimination'},
            'player_one_config': experiment_config.get('player_one_config', {}),
            'player_two_config': experiment_config.get('player_two_config', {}),
        })
        # Run the game
        final_state = run_game(initial_state)
        # Save the result
        save_game_result(final_state, results_dir, iteration=i+1)
        # Collect results for analysis
        experiment_results.append(final_state)
    return experiment_results

def save_game_result(game_state: GameState, results_dir: Path, iteration: int):
    # Serialize the game_state (e.g., as YAML) and save it
    iteration_dir = results_dir / f'iteration_{iteration}'
    iteration_dir.mkdir(parents=True, exist_ok=True)
    game_state_path = iteration_dir / 'final_state.yaml'
    with open(game_state_path, 'w') as f:
        yaml.dump(game_state.to_dict(), f)

def main():
    configs_dir = Path('configs')
    for config_file in configs_dir.glob('*.yaml'):
        print(f"Starting experiment with config: {config_file.name}")
        experiment_config = load_experiment_config(str(config_file))
        results_dir = setup_experiment_environment(experiment_config)
        run_experiment(experiment_config, results_dir)

if __name__ == "__main__":
    main() 