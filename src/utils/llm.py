# Imports
import yaml
import os
from typing import List, Dict, Any, Tuple
from anthropic import Anthropic
from string import Template

def load_prompt_from_file(prompt_path: str) -> str:
  with open(prompt_path, 'r') as f:
    return f.read()

def load_game_prompts(filename: str) -> str:
  prompt_path = f"src/prompts/{filename}"
  try:
    return load_prompt_from_file(prompt_path)
  except FileNotFoundError:
    raise FileNotFoundError(f"Could not find prompt file at {prompt_path}")

# Functions
def call_llm_api(message_chain: List[Dict[str, str]]) -> str:
  system_message, updated_chain = extract_system_message(message_chain)

  try:
    client = Anthropic()
    response = client.messages.create(
      model="claude-3-5-sonnet-20240620",
      max_tokens=4096,
      temperature=0.0,
      messages=updated_chain,
      system=system_message
    )
    
    # Check response status
    if hasattr(response, 'status_code') and response.status_code != 200:
        print(f"Warning: LLM API returned non-200 status code: {response.status_code}")
        print(f"Response payload: {response}")
        return ""  # Return empty string on error
        
    return process_model_output(response)
  except Exception as e:
    print(f"Error calling Anthropic API: {str(e)}")
    print(f"Full error details: {e}")
    return ""

def create_message_chain(prompt_input: str | List[Dict[str, str]], variables: Dict[str, Any] = None) -> List[Dict[str, str]]:
    # If input is already a list of messages, just process variables if needed
    if isinstance(prompt_input, list):
        return prompt_input
        
    # Otherwise treat as file path
    try:
        with open(prompt_input, 'r') as f:
            template_text = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find prompt file at {prompt_input}")
    
    # Convert variables to YAML string format if they exist
    if variables:
        try:
            for key, value in variables.items():
                if isinstance(value, dict):
                    # Convert dict to YAML string with preserved formatting
                    yaml_str = yaml.dump(value, sort_keys=False, default_flow_style=False)
                    # Indent the YAML string
                    indented_yaml = '\n'.join('    ' + line for line in yaml_str.splitlines())
                    variables[key] = indented_yaml
            template = Template(template_text)
            template_text = template.substitute(variables)
        except KeyError as e:
            raise KeyError(f"Missing template variable in prompt: {e}")
    
    # Convert formatted text to YAML structure
    try:
        template = yaml.safe_load(template_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format in prompt file: {e}")
    
    # Create message chain from YAML
    message_chain = [{'role': msg['role'], 'content': msg['content']} for msg in template]
    
    # Strip trailing whitespace from last assistant message if present
    if message_chain and message_chain[-1]['role'] == 'assistant':
        message_chain[-1]['content'] = message_chain[-1]['content'].rstrip()
    
    return message_chain

def extract_system_message(message_chain: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
  system_message = ""
  updated_chain = []
  for message in message_chain:
    if message['role'] == 'system':
      system_message = message['content']
    else:
      updated_chain.append(message)
  return system_message, updated_chain

def process_model_output(response: Any) -> str:
  return response.content[0].text

def pretty_print_message_chain(message_chain: List[Dict[str, str]]) -> None:
    print("\n\n" + "-" * 40)
    print("Generated prompt chain:")
    print("Messages:")
    for idx, message in enumerate(message_chain, 1):
        print(f"\n{idx}. Message:")
        print(f"Role: {message['role']}")
        print(f"Content:\n      {message['content'].replace('\n', '\n      ')}")

# Main section with example usage
if __name__ == "__main__":
  # Example 1: Using YAML template directly
  yaml_template = """
  - name: system instructions
    role: system
    content: |
      You are a concise software engineer assistant. Here are some suggestions:
      - You get straight to the point and do not waste any words.
      - Do not add any pleasantries in your response.

  - name: example 1 query
    role: user
    content: |
      Tell me 3 facts about the color red.
  """

  message_chain = create_message_chain(yaml_template)
  print("Example 1 - Created message chain from YAML:")
  pretty_print_message_chain(message_chain)
  api_response = call_llm_api(message_chain)
  print("\nAPI Response:")
  print(api_response)

  # Example 2: Loading prompt from file
  print("\n" + "="*50 + "\n")
  prompt_path = "prompts/test.txt"
  try:
    file_yaml = load_prompt_from_file(prompt_path)
    file_message_chain = create_message_chain(file_yaml)
    print("Example 2 - Created message chain from file:")
    pretty_print_message_chain(file_message_chain)
    file_api_response = call_llm_api(file_message_chain)
    print("\nAPI Response:")
    print(file_api_response)
  except FileNotFoundError:
    print(f"Error: Could not find prompt file at {prompt_path}")