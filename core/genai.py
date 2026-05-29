import json
import requests
import os
import sys
from pathlib import Path
from core.intent import detect_intent
from core.memory import remember_short, get_short_term, load_long_term, save_fact, recall_fact, forget_fact

# --- The API key is no longer needed in this file ---
# It is now securely handled by your Node.js server.
# keys = json.loads(Path("config/keys.json").read_text())
# API_KEY = keys["gemini"]

def process_with_gpt(prompt):
    # --- The request now goes to your local Node.js server ---
    # This server will securely add the API key and forward the request to Google.
    middle_server_url = "https://aura-backend-6upw.onrender.com/api/aura"

    # The API key header is no longer needed here.
    headers = {
        "Content-Type": "application/json",
    }

    # The logic for building the prompt and the request body remains exactly the same.
    system_instruction = (
        "You are A.U.R.A., an AI operating system .\n\n"
        "Your role is to generate directly executable Python system commands based on the detected intent and the user's input.\n\n"
        "Rules:\n"
        "- Always generate syntactically valid Python commands.\n"
        "- Use os.system() as the primary method to execute commands.\n"
        "- Use NirCmd inside os.system() for system-level tasks like volume control, brightness, sending keystrokes, taking screenshots, etc.\n"
        "- Use start command to open applications websites whenever possible.\n"
        "- You can use PowerShell commands for advanced file handling and automation."
        "- When using PowerShell inside os.system(), use double single quotes ('') around the wildcard string to escape properly inside Python raw strings."
        "- Use standard Python with os/system libraries.\n"
        "- Windows file paths must use raw strings (prefix commands with r'' when backslashes are used).\n"
        "- Respond only with a valid JSON object using single quotes for all string values to avoid escape issues."
        "- Do not insert (\\n) characters inside Python commands.\n"
        "- If no action is needed, leave the 'command' field as an empty string.\n\n"
        "Output strictly in this JSON format:\n"
        "{\n"
        '  "command": "<python_code_or_action using os.system()>",\n'
        '  "description": "<brief natural language reply to the user>"\n'
        "}\n\n"
        "DO NOT explain.\n"
        "DO NOT use markdown.\n"
        "DO NOT include any extra text.\n"
        "Reply only in valid JSON format."
    )

    # Prepare prompt parts
    parts = [{"text": system_instruction}]
    for k, v in load_long_term().items():
        parts.append({"text": f"Memory - {k}: {v}"})

    for m in get_short_term():
        parts.append({"text": f"User: {m['user']}"})
        parts.append({"text": f"AURA: {m['aura']}"})

    parts.append({"text": f"User: {prompt}"})

    # This is the request body that will be sent to your Node.js server.
    data = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }

    try:
        # The request is now sent to your local server.
        res = requests.post(
            middle_server_url,
            headers=headers,
            json=data
        )
        # Ensure the request was successful
        res.raise_for_status() 
        
        # The rest of the logic is the same, as the server forwards the API's response structure.
        res_json = res.json()

        # The server should have already parsed the content, but we handle it here just in case.
        if "command" in res_json and "description" in res_json:
            remember_short(prompt, res_json["description"])
            return res_json
        else:
            # This case handles if the server forwards a different structure, like an error from Google.
            print("⚠️ Unexpected response format from server:", res_json)
            return {
                "command": "",
                "description": "Received an unexpected response from the server."
            }

    except requests.exceptions.RequestException as e:
        print("⚠️ Error connecting to the middle server:", e)
        return {
            "command": "",
            "description": f"Error: Could not connect to the AURA backend server at {middle_server_url}. Is it running?"
        }
    except Exception as e:
        print("⚠️ An unexpected error occurred:", e)
        return {
            "command": "",
            "description": f"An unexpected error occurred: {str(e)}"
        }

def handle_memory_intent(intent, user_input):
    if "memory save" in intent or "remember" in intent:
        try:
            key, value = user_input.split("is", 1)
            key = key.replace("remember", "").strip()
            value = value.strip()
            save_fact(key, value)
            return f"I've remembered {key} as {value}.", ""
        except Exception:
            return "I couldn't understand what to remember.", ""
    elif "memory recall" in intent or "what is" in user_input.lower():
        key = user_input.lower().replace("what is", "").strip()
        value = recall_fact(key)
        if value:
            return f"{key.capitalize()} is {value}.", ""
        else:
            return f"I don't remember {key}.", ""
    elif "forget" in intent:
        key = user_input.lower().replace("forget", "").strip()
        forget_fact(key)
        return f"I've forgotten {key}.", ""
    else:
        return None, None

def aura_brain(user_input):
    intent, confidence = detect_intent(user_input)

    # Step 1: Handle memory commands locally
    response_text, command = handle_memory_intent(intent, user_input)
    if response_text:
        return {"description": response_text, "command": command}

    # Step 2: Send other commands to the middle server
    formatted_prompt = (
        f"User Intent: {intent}\n"
        f"User Input: {user_input}\n\n"
        "Based on the above, generate either:\n"
        "- a Python os.system(...) command,\n"
        "- OR a useful text response to the user.\n"
        "Output in strict JSON format as explained."
    )

    return process_with_gpt(formatted_prompt)

if __name__ == "__main__":
    print("🔵 AURA Assistant (type 'exit' or 'quit' to stop)")
    while True:
        user_input = input("🗣️ User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting AURA...")
            break

        response = aura_brain(user_input)
        print(f"🤖 AURA: {response.get('description', 'No response')}")
        print(f"📟 Command: {response.get('command', 'No command')}")
