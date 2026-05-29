import os
import re
import json
from pathlib import Path
from core.speak import speak
from core.memory import recall_fact, save_fact

# ---------- Paths ----------
SKILLS_FILE = Path("memory/skills.json")
COMMAND_HISTORY_FILE = Path("memory/command_history.json")
CONTEXT_FILE = Path("memory/context_skills.json")

# ---------- Ensure Files Exist ----------
SKILLS_FILE.parent.mkdir(parents=True, exist_ok=True)
if not SKILLS_FILE.exists():
    SKILLS_FILE.write_text(json.dumps({}, indent=2))
if not COMMAND_HISTORY_FILE.exists():
    COMMAND_HISTORY_FILE.write_text(json.dumps([], indent=2))
if not CONTEXT_FILE.exists():
    CONTEXT_FILE.write_text(json.dumps({}, indent=2))

# ---------- Command History ----------
def save_command_to_history(command, description):
    history = json.loads(COMMAND_HISTORY_FILE.read_text())
    history.append({"command": command, "description": description})
    if len(history) > 100:
        history.pop(0)
    COMMAND_HISTORY_FILE.write_text(json.dumps(history, indent=2))

# ---------- Skills ----------
def load_skills():
    return json.loads(SKILLS_FILE.read_text())

def save_skill(trigger, command):
    skills = load_skills()
    skills[trigger.lower()] = command
    SKILLS_FILE.write_text(json.dumps(skills, indent=2))

def forget_skill(trigger):
    skills = load_skills()
    trigger = trigger.lower()
    if trigger in skills:
        del skills[trigger]
        SKILLS_FILE.write_text(json.dumps(skills, indent=2))
        return True
    return False

def list_skills():
    return list(load_skills().keys())

def replace_skill(trigger, new_command):
    save_skill(trigger, new_command)

def match_learned_command(user_input):
    return load_skills().get(user_input.lower())

# ---------- Contexts ----------
def load_contexts():
    return json.loads(CONTEXT_FILE.read_text())

def save_context(trigger, steps):
    contexts = load_contexts()
    contexts[trigger.lower()] = steps
    CONTEXT_FILE.write_text(json.dumps(contexts, indent=2))

def run_context(trigger):
    steps = load_contexts().get(trigger.lower())
    if not steps:
        speak(f"⚠️ I don't know how to handle: {trigger}")
        return
    speak(f"🔄 Executing context: {trigger}")
    for step in steps:
        execute(step, description=step)

# ---------- Security Check ----------
def is_safe(command):
    unsafe_patterns = [
        r"os\.system\(['\"]shutdown",
        r"os\.system\(['\"]taskkill",
        r"os\.remove",
        r"os\.rmdir",
        r"shutil\.rmtree",
        r"__import__",
        r"exec\(",
        r"eval\("
    ]
    return not any(re.search(pattern, command) for pattern in unsafe_patterns)

# ---------- Main Execution ----------
def execute(command, description=""):
    speak(f"AURA 🟢: {description}")
    save_command_to_history(command, description)

    try:
        if not isinstance(command, str):
            raise TypeError("Command must be a string.")

        # Handle memory commands dynamically
        if command.startswith("memory:recall_fact:"):
            key = command.split(":", 2)[-1]
            value = recall_fact(key)
            if value:
                speak(f"Your {key} is {value}.")
            else:
                speak(f"I don’t know your {key} yet.")
            return

        elif command.startswith("memory:save_fact:"):
            _, _, key, value = command.split(":", 3)
            save_fact(key, value)
            speak(f"I'll remember your {key} as {value}.")
            return

        # Handle skill/context commands
        elif command.startswith("learn:"):
            _, trigger, code = command.split(":", 2)
            if is_safe(code):
                save_skill(trigger, code)
                speak(f"✅ Learned skill: '{trigger}'")
            else:
                speak("⚠️ Unsafe skill blocked.")
            return

        elif command.startswith("forget_skill:"):
            trigger = command.split(":", 1)[1]
            if forget_skill(trigger):
                speak(f"🗑️ Forgot skill '{trigger}'.")
            else:
                speak(f"⚠️ No such skill '{trigger}'.")
            return

        elif command == "list_skills":
            skills = list_skills()
            speak("📋 Learned skills: " + ", ".join(skills) if skills else "No skills learned.")
            return

        elif command.startswith("replace_skill:"):
            _, trigger, new_code = command.split(":", 2)
            if is_safe(new_code):
                replace_skill(trigger, new_code)
                speak(f"🔁 Skill '{trigger}' replaced.")
            else:
                speak("⚠️ Unsafe replacement blocked.")
            return

        elif command.startswith("context:learn:"):
            _, _, trigger, steps_str = command.split(":", 3)
            steps = [s.strip() for s in steps_str.split(",")]
            save_context(trigger, steps)
            speak(f"📚 Context '{trigger}' learned.")
            return

        elif command.startswith("context:run:"):
            _, _, trigger = command.split(":", 2)
            run_context(trigger)
            return

        # Execute learned commands if matched
        learned = match_learned_command(command)
        if learned:
            command = learned

        # Validate before executing
        if not is_safe(command):
            speak("⚠️ Unsafe command blocked.")
            return

        exec_globals = {"os": os}
        exec(command, exec_globals)

    except Exception as e:
        print("AURA 🔴 Error executing command:", e)
