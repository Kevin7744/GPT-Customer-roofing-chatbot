import json
import requests
import os
import openai
from prompts import formatter_prompt, assistant_instructions

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']

client = openai(api_key=OPENAI_API_KEY)

# Add lead to airtable
def create_lead(name, phone, address):
  url = "https://api.airtable.com/v0/app055RVfBPnDrQmd/Leads"  # Change this to your Airtable API URL
  headers = {
      "Authorization": AIRTABLE_API_KEY,
      "Content-Type": "application/json"
  }
  data = {
      "records": [{
          "fields": {
              "Name": name,
              "Phone": phone,
              "Address": address
          }
      }]
  }
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200:
    print("Lead created successfully.")
    return response.json()
  else:
    print(f"Failed to create lead: {response.text}")

# Main calculation function for solar data output
def roofing_cost_estimation():
  print(f"Calculating roofing potential ")


# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file already, then load that assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    file = client.files.create(file=open("knowledge.docx", "rb"),purpose='assistants')
    
    assistant = client.beta.assistants.create(
        instructions=assistant_instructions,
        model="gpt-4-1106-preview",
        tools=[
            {
                "type": "retrieval"  # This adds the knowledge base as a tool
            },
            {
                "type": "function",  # This adds the solar calculator as a tool
                "function": {
                    "name": "roofing_cost_estimation",
                    "description": "",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            # "address": {
                            #     "type":"string",
                            #     "description": "Address for calculating solar potential."
                            # },
                            # "monthly_bill": {
                            #     "type":"integer",
                            #     "description": "Monthly electricity bill in USD for savings estimation."
                            # }
                        },
                        # "required": ["address", "monthly_bill"]
                    }
                }
            },
            {
                "type": "function",  # This adds the lead capture as a tool
                "function": {
                    "name": "create_lead",
                    "description": "Capture lead details and save to Airtable.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the lead."
                            },
                            "phone": {
                                "type": "string",
                                "description": "Phone number of the lead."
                            },
                            "address": {
                                "type": "string",
                                "description": "Address of the lead."
                            }
                        },
                        "required": ["name", "phone", "address"]
                    }
                }
            }
        ],
        file_ids=[file.id])

    # Create a new assistant.json file to load on future runs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id