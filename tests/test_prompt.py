import pytest
from pathlib import Path
from utils.prompt import PromptComposer, generate_prompt_chain
import yaml

@pytest.fixture
def prompt_composer():
    return PromptComposer("src/prompts")

def test_load_prompt_file(prompt_composer):
    content = prompt_composer.load_prompt_file("test_1.txt")
    expected = """- name: test_system_prompt
  role: system
  content: You are a helpful assistant.
"""
    assert content.strip() == expected.strip()

def test_compose_prompt_basic(prompt_composer):
    configs = [{
        'prompt_filepath': 'test_1.txt'
    }]
    
    result = prompt_composer.compose_prompt(configs)
    
    assert len(result) == 1
    assert result[0]['role'] == 'system'
    assert result[0]['content'] == 'You are a helpful assistant.'

def test_compose_prompt_multiple_files(prompt_composer):
    configs = [
        {'prompt_filepath': 'test_1.txt'},
        {'prompt_filepath': 'test_2.txt',
         'template_params': {'world_representation': 'test world'}}
    ]
    
    result = prompt_composer.compose_prompt(configs)
    
    assert len(result) == 2
    assert result[0]['role'] == 'system'
    assert result[1]['role'] == 'user'
    assert 'test world' in result[1]['content']