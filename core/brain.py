import json
import requests
from pathlib import Path
from core.intent import detect_intent
from core.memory import remember_short, get_short_term, load_long_term, save_fact, recall_fact, forget_fact

# Load OpenRouter API key
keys = json.loads(Path("config/keys.json").read_text())
API_KEY = keys["openai"]

def process_with_gpt(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aura.local"  # optional
    }

    messages = [
    {
        "role": "system",
        "content": (
            "You are A.U.R.A., an AI operating system assistant.\n\n"
            "Your role is to generate directly executable Python system commands based on the detected intent and the user's input.\n\n"
            "Rules:\n"
            "- Always generate syntactically valid Python commands.\n"
            "- Use os.system() as the primary method to execute commands.\n"
            "- Prioritize using NirCmd inside os.system() for system-level tasks like volume control, brightness, opening URLs, sending keystrokes, taking screenshots, etc.\n"
            "- Use standard Python with os/system libraries only when NirCmd cannot handle the task.\n"
            "- Windows file paths must use raw strings (prefix commands with r'' when backslashes are used).\n"
            "- Do not insert '\\n' characters inside Python commands.\n"
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
    }
]


    # Append memory context
    for k, v in load_long_term().items():
        messages.append({"role": "system", "content": f"{k}: {v}"})

    for m in get_short_term():
        messages.append({"role": "user", "content": m["user"]})
        messages.append({"role": "assistant", "content": m["aura"]})

    messages.append({"role": "user", "content": prompt})

    data = {
        "model": "openai/gpt-4.1",
        "max_tokens": 1000,
        "messages": messages
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        res_json = res.json()

        if "choices" in res_json:
            content = res_json["choices"][0]["message"]["content"]
            remember_short(prompt, content)
            return json.loads(content)
        else:
            raise Exception(res_json.get("error", {}).get("message", "Unknown response error"))

    except Exception as e:
        print("⚠️ OpenRouter error:", e)
        print("Response:", res.text if 'res' in locals() else 'No response')
        return {
            "command": "",
            "description": f"Error: {str(e)}"
        }

def handle_memory_intent(intent, user_input):
    if "memory save" in intent or "remember" in intent:
        # Example: "remember my name is Shubham"
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

    # Step 2: Send other commands to GPT
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
