from typing import List, Dict, Any
import yaml
from pathlib import Path

class PromptComposer:
    def __init__(self, prompts_dir: str = "src/prompts"):
        self.prompts_dir = Path(prompts_dir)
        
    def load_prompt_file(self, filepath: str) -> str:
        full_path = self.prompts_dir / filepath
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find prompt file at {full_path}")

    def compose_prompt(self, prompt_configs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Composes multiple prompts into a single message chain based on config
        """
        composed_chain = []
        
        for config in prompt_configs:
            prompt_content = self.load_prompt_file(config['prompt_filepath'])
            
            # Apply template parameters if they exist
            if 'template_params' in config:
                try:
                    # Convert any dict params to YAML format
                    template_params = config['template_params'].copy()
                    for key, value in template_params.items():
                        if isinstance(value, dict):
                            yaml_str = yaml.dump(value, sort_keys=False, default_flow_style=False)
                            template_params[key] = '\n'.join('    ' + line for line in yaml_str.splitlines())
                    
                    # Apply template substitution
                    prompt_content = prompt_content.format(**template_params)
                    
                except KeyError as e:
                    raise KeyError(f"Missing template parameter in prompt {config['prompt_filepath']}: {e}")
            
            # Parse the YAML content
            try:
                prompt_messages = yaml.safe_load(prompt_content)
                if isinstance(prompt_messages, list):
                    composed_chain.extend(prompt_messages)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format in prompt file {config['prompt_filepath']}: {e}")
                
        return composed_chain

def generate_prompt_chain(prompt_configs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    composer = PromptComposer()
    return composer.compose_prompt(prompt_configs) 