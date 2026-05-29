import json
import requests
import os
import sys
from pathlib import Path
from core.intent import detect_intent
from core.memory import remember_short, get_short_term, load_long_term, save_fact, recall_fact, forget_fact

def resource_path(relative_path):
    """Get absolute path to resource, works for PyInstaller .exe and normal script."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

# Load Groq API key
config_path = resource_path("config/keys.json")
with open(config_path, "r") as f:
    keys = json.load(f)


#keys = json.loads(Path("config/keys.json").read_text())
API_KEY = keys["groq"]

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"

def process_with_groq(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = (
        "You are A.U.R.A., an AI operating system .\n\n"
        "Your role is to generate directly executable Python system commands based on the detected intent and the user's input.\n\n"
        "Rules:\n"
        "- Always generate syntactically valid Python commands.\n"
        "- Use os.system() as the primary method to execute commands.\n"
        "- Use NirCmd inside os.system() for system-level tasks like volume control, brightness, sending keystrokes, taking screenshots, etc.\n"
        "- Use start command to open applications websites whenever possible.\n"
        "- You can use PowerShell commands for advanced file handling and automation."
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

    messages = [{"role": "system", "content": system_message}]

    for k, v in load_long_term().items():
        messages.append({"role": "system", "content": f"{k}: {v}"})
    for m in get_short_term():
        messages.append({"role": "user", "content": m["user"]})
        messages.append({"role": "assistant", "content": m["aura"]})

    messages.append({"role": "user", "content": prompt})

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 1,
        "max_tokens": 2000,
        "top_p": 1,
        "stream": False,
        "stop": None,
    }

    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=data)
        res_json = res.json()

        if "choices" in res_json:
            content = res_json["choices"][0]["message"]["content"]
            remember_short(prompt, content)
            return json.loads(content)
        else:
            raise Exception(res_json.get("error", {}).get("message", "Unknown error"))

    except Exception as e:
        print("⚠️ Groq API error:", e)
        print("Response:", res.text if 'res' in locals() else 'No response')
        return {
            "command": "",
            "description": f"Error: {str(e)}"
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
    print(f"🎯 Detected Intent: {intent} (Confidence: {confidence:.2f})")

    response_text, command = handle_memory_intent(intent, user_input)
    if response_text:
        return {"description": response_text, "command": command}

    formatted_prompt = (
        f"User Intent: {intent}\n"
        f"User Input: {user_input}\n\n"
        "Based on the above, generate either:\n"
        "- a Python os.system(...) command,\n"
        "- OR a useful text response to the user.\n"
        "Output in strict JSON format as explained."
    )

    return process_with_groq(formatted_prompt)

if __name__ == "__main__":
    print("🔵 AURA Assistant (Groq API Mode - type 'exit' or 'quit' to stop)")
    while True:
        user_input = input("🗣️ User: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting AURA...")
            break

        response = aura_brain(user_input)
        print(f"🤖 AURA: {response.get('description', 'No response')}")
        print(f"📟 Command: {response.get('command', 'No command')}")
