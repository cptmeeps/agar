import pytest
import yaml
from string import Template
from unittest.mock import patch, MagicMock
from utils.llm import (
    load_prompt_from_file,
    load_game_prompts,
    call_llm_api,
    create_message_chain,
    extract_system_message,
    process_model_output
)

@pytest.fixture
def sample_yaml_content():
    return """
    - name: system message
      role: system
      content: You are a helpful assistant.

    - name: user query
      role: user
      content: Tell me about Python.

    - name: assistant response
      role: assistant
      content: Python is a programming language.
    """

@pytest.fixture
def sample_message_chain():
    return [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'Tell me about Python.'},
        {'role': 'assistant', 'content': 'Python is a programming language.'}
    ]

def test_load_prompt_from_file(tmp_path):
    # Create a temporary file with test content
    test_file = tmp_path / "test_prompt.txt"
    test_content = "Test prompt content"
    test_file.write_text(test_content)
    
    result = load_prompt_from_file(str(test_file))
    assert result == test_content

def test_load_prompt_from_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_prompt_from_file("nonexistent_file.txt")

def test_load_game_prompts(tmp_path, monkeypatch):
    # Create src/prompts directory structure in temp path
    prompts_dir = tmp_path / "src" / "prompts"
    prompts_dir.mkdir(parents=True)
    
    # Create test prompt file
    test_file = prompts_dir / "test.txt"
    test_content = """- name: system instructions
  role: system
  content: Test system message

- name: user query
  role: user
  content: Test user message"""
    
    test_file.write_text(test_content)
    
    # Temporarily modify the system path
    monkeypatch.chdir(tmp_path)
    
    result = load_game_prompts("test.txt")
    assert result == test_content

def test_create_message_chain_basic(sample_yaml_content, tmp_path):
    prompt_file = tmp_path / "prompt.yml"
    prompt_file.write_text(sample_yaml_content)
    
    message_chain = create_message_chain(str(prompt_file))
    assert len(message_chain) == 3
    assert message_chain[0]['role'] == 'system'
    assert message_chain[1]['role'] == 'user'
    assert message_chain[2]['role'] == 'assistant'

def test_create_message_chain_with_variables(tmp_path):
    template_content = """
    - name: test
      role: user
      content: Hello ${name}, your score is ${score}
    """
    prompt_file = tmp_path / "prompt.yml"
    prompt_file.write_text(template_content)
    
    variables = {'name': 'Alice', 'score': '100'}
    message_chain = create_message_chain(str(prompt_file), variables)
    
    assert message_chain[0]['content'] == 'Hello Alice, your score is 100'
