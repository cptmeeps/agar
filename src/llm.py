# Imports
import yaml
import os
from typing import List, Dict, Any, Tuple
from anthropic import Anthropic



def load_prompt_from_file(prompt_path: str) -> str:
  with open(prompt_path, 'r') as f:
    return f.read()

# Functions
def call_llm_api(message_chain: List[Dict[str, str]]) -> str:
  # pretty_print_message_chain(message_chain)
  system_message, updated_chain = extract_system_message(message_chain)

  try:
    client = Anthropic()
    response = client.messages.create(
      model="claude-3-5-sonnet-20240620",
      max_tokens=4096,
      temperature=0.1,
      messages=updated_chain,
      system=system_message
    )
    return process_model_output(response)
  except Exception as e:
    return f"Error calling Anthropic API: {str(e)}"

def create_message_chain(yaml_template: str) -> List[Dict[str, str]]:
  template = yaml.safe_load(yaml_template)
  message_chain = [{'role': msg['role'], 'content': msg['content']} for msg in template]

  # Check if the last message is from the assistant and strip trailing whitespace
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
  for i, message in enumerate(message_chain):
    print(f"Message {i + 1}:")
    print(f"  Role: {message['role']}")
    print(f"  Content:\n{message['content']}")
    print("-" * 50)

def load_game_prompts() -> str:
    prompt_path = "src/prompts/game_prompts.yaml"
    with open(prompt_path, 'r') as f:
        return f.read()

def create_strategic_prompt(game_state: GameState, player_id: int) -> List[Dict[str, str]]:
    # Get the world representation
    world_representation = create_llm_world_representation(game_state, player_id)
    
    # Load and prepare the prompt template
    prompt_template = load_game_prompts()
    game_state_yaml = yaml.dump(world_representation, sort_keys=False)
    
    # Create the message chain
    message_chain = create_message_chain(prompt_template)
    
    # Find and update the game state analysis message
    for message in message_chain:
        if message['role'] == 'user':
            message['content'] = message['content'].format(
                game_state_yaml=game_state_yaml
            )
    
    return message_chain

def get_ai_moves(game_state: GameState, player_id: int) -> Dict[str, Any]:
    """
    Gets strategic moves from the LLM for the specified player.
    """
    message_chain = create_strategic_prompt(game_state, player_id)
    response = call_llm_api(message_chain)
    
    try:
        # Parse the response into the expected move format
        moves = yaml.safe_load(response)
        return moves
    except yaml.YAMLError:
        # Fallback to empty moves if parsing fails
        return {"moves": []}

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