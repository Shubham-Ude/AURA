# core/skills.py
import json
from pathlib import Path

SKILLS_FILE = Path("memory/skills.json")
SKILLS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Load skills from disk
def load_skills():
    if SKILLS_FILE.exists():
        return json.loads(SKILLS_FILE.read_text())
    return {}

# Save skills to disk
def save_skills(skills):
    SKILLS_FILE.write_text(json.dumps(skills, indent=2))

# Add or update a skill
def learn_skill(trigger, command, description=""):
    skills = load_skills()
    skills[trigger.lower()] = {
        "command": command,
        "description": description
    }
    save_skills(skills)

# Get a skill if exists
def recall_skill(trigger):
    return load_skills().get(trigger.lower())
