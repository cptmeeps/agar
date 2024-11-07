from typing import List, Dict, Any
import yaml
from pathlib import Path
from string import Template
import json

class PromptComposer:
    def __init__(self, prompts_dir: str = "src/prompts"):
        self.prompts_dir = Path(prompts_dir)
        
    def load_prompt_file(self, filepath: str) -> str:
        full_path = self.prompts_dir / filepath
        with open(full_path, 'r') as f:
            return f.read()

    def compose_prompt(self, prompt_configs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        composed_chain = []
        
        for config in prompt_configs:
            # Load the raw prompt content
            prompt_content = self.load_prompt_file(config['prompt_filepath'])
            
            # First apply template parameters if they exist
            if 'template_params' in config:
                template_params = config['template_params'].copy()
                # Convert any dictionary values to YAML strings AND indent them properly
                for key, value in template_params.items():
                    if isinstance(value, dict):
                        # Convert to YAML and indent each line by 4 spaces
                        yaml_str = yaml.dump(value, default_flow_style=False)
                        indented_yaml = '\n'.join('    ' + line for line in yaml_str.splitlines())
                        template_params[key] = indented_yaml
                
                # Use Template for ${variable} syntax
                template = Template(prompt_content)
                try:
                    prompt_content = template.substitute(template_params)
                except KeyError as e:
                    raise KeyError(f"Missing template variable in prompt: {e}")
            # print(prompt_content)
            # Then parse the templated content as YAML
            prompt_messages = yaml.safe_load(prompt_content)
            if isinstance(prompt_messages, list):
                filtered_messages = [
                    {'role': msg['role'], 'content': msg['content']}
                    for msg in prompt_messages
                ]
                composed_chain.extend(filtered_messages)
                
        return composed_chain

def generate_prompt_chain(prompt_configs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    composer = PromptComposer()
    return composer.compose_prompt(prompt_configs) 

def main():
    print("\n" + "="*80)
    print("Testing PromptComposer")
    print("="*80)
    
    # Initialize PromptComposer with the prompts directory
    composer = PromptComposer("src/prompts")
    
    print("\n1. Testing load_prompt_file")
    print("Expected: Should load the content of test.txt")
    try:
        content = composer.load_prompt_file("test.txt")
        print("\nLoaded content:")
        print(content)
        print("✅ Successfully loaded prompt file")
    except Exception as e:
        print(f"❌ Error loading prompt file: {str(e)}")
    
    print("\n2. Testing compose_prompt with template parameters")
    print("Expected: Should replace template variables and return formatted message chain")
    
    # Create a sample world representation matching the format in input_action.py
    example_world_representation = {
        "game_info": {
            "current_turn": 1,
            "max_turns": 10,
            "game_status": "in_progress"
        },
        "board": {
            "controlled_territories": {
                "your_territory": [
                    {"x": 0, "y": 2}
                ],
                "enemy_territory": [
                    {"x": 4, "y": 2}
                ]
            },
            "cells": {
                "0,2": {
                    "position": {"x": 0, "y": 2},
                    "units": {
                        "your_units": 2,
                        "enemy_units": 0
                    },
                    "controlled_by": "you"
                }
                # ... other cells would go here
            }
        }
    }

    test_configs = [{
        'prompt_filepath': 'test.txt',
        'template_params': {
            'world_representation': example_world_representation
        }
    }]
    
    # Generate prompt chain
    prompt_chain = generate_prompt_chain(test_configs)
    
    print("\nGenerated prompt chain:")
    print("Messages:")
    for idx, message in enumerate(prompt_chain, 1):
        print(f"\n{idx}. Message:")
        print(f"Role: {message['role']}")
        print(f"Content:\n  {message['content'].replace('\n', '\n      ')}")
    print("\n✅ Successfully generated prompt chain")

if __name__ == "__main__":
    main()    