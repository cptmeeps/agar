from typing import List, Dict, Any
import yaml
from pathlib import Path
from string import Template

class PromptComposer:
    def __init__(self, prompts_dir: str = "src/prompts"):
        self.prompts_dir = Path(prompts_dir)
        
    def load_prompt_file(self, filepath: str) -> str:
        full_path = self.prompts_dir / filepath
        with open(full_path, 'r') as f:
            return f.read()

    def compose_prompt(self, prompt_configs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Composes multiple prompts into a single message chain based on config
        """
        composed_chain = []
        
        for config in prompt_configs:
            prompt_content = self.load_prompt_file(config['prompt_filepath'])
            
            # Apply template parameters if they exist
            if 'template_params' in config:
                # Convert any dict params to YAML format
                template_params = config['template_params'].copy()
                for key, value in template_params.items():
                    if isinstance(value, dict):
                        yaml_str = yaml.dump(value, sort_keys=False, default_flow_style=False)
                        indented_yaml = '\n'.join('    ' + line for line in yaml_str.splitlines())
                        template_params[key] = indented_yaml
                
                # Use Template for ${variable} syntax
                template = Template(prompt_content)
                try:
                    prompt_content = template.substitute(template_params)
                except KeyError as e:
                    raise KeyError(f"Missing template variable in prompt: {e}")
            
            # Parse the YAML content
            prompt_messages = yaml.safe_load(prompt_content)
            if isinstance(prompt_messages, list):
                # Filter to only include role and content fields
                filtered_messages = [
                    {'role': msg['role'], 'content': msg['content']}
                    for msg in prompt_messages
                ]
                composed_chain.extend(filtered_messages)
                
        return composed_chain

def generate_prompt_chain(prompt_configs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    composer = PromptComposer()
    return composer.compose_prompt(prompt_configs) 