# Imports
import yaml
from typing import List, Dict, Any, Tuple
from anthropic import Anthropic

# Functions
def call_llm_api(message_chain: List[Dict[str, str]]) -> str:
  # pretty_print_message_chain(message_chain)
  system_message, updated_chain = extract_system_message(message_chain)

  try:
    client = Anthropic()
    response = client.messages.create(
      model="claude-3-5-sonnet-20240620",
      max_tokens=4096,
      temperature=0.3,
      messages=updated_chain,
      system=system_message
    )
    return process_model_output(response)
  except Exception as e:
    return f"Error calling Anthropic API: {str(e)}"

def create_message_chain(yaml_template: str) -> List[Dict[str, str]]:
  """Creates a message chain from a YAML string template."""
  template = yaml.safe_load(yaml_template)
  message_chain = [{'role': msg['role'], 'content': msg['content']} for msg in template]

  # Check if the last message is from the assistant and strip trailing whitespace
  if message_chain and message_chain[-1]['role'] == 'assistant':
    message_chain[-1]['content'] = message_chain[-1]['content'].rstrip()

  return message_chain

def extract_system_message(message_chain: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
  """Extracts the system message from the message chain."""
  system_message = ""
  updated_chain = []
  for message in message_chain:
    if message['role'] == 'system':
      system_message = message['content']
    else:
      updated_chain.append(message)
  return system_message, updated_chain

def process_model_output(response: Any) -> str:
  """Processes the output from the Anthropic API."""
  return response.content[0].text

def pretty_print_message_chain(message_chain: List[Dict[str, str]]) -> None:
  """Pretty prints the message chain for easy examination."""
  for i, message in enumerate(message_chain):
    print(f"Message {i + 1}:")
    print(f"  Role: {message['role']}")
    print(f"  Content:\n{message['content']}")
    print("-" * 50)

# Main section with example usage
if __name__ == "__main__":
  # Example usage of create_message_chain
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
  print("Created message chain:")
  # pretty_print_message_chain(message_chain)

  # Example usage loading yaml from doc
  drive_service, doc_service, sheets_service = authenticate()
  folder_path = '/content/drive/My Drive/mtc/prompts'
  doc_id = '1rOfUxEsLdjREYG0uP0wL2Mnp0u02Hv3Zr_8SamTvVBk' # test_key_ideas
  prompt_template = read_doc(doc_service, doc_id)
  message_chain = create_message_chain(prompt_template)
  print("Message chain from document:")
  pretty_print_message_chain(message_chain)

  # Example usage of call_llm_api
  api_response = call_llm_api(message_chain)
  print("\nAPI Response:")
  print(api_response)