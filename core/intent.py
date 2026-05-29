import os
import sys
import requests
import json
from pathlib import Path

# ---------- Helper: Get Correct Path for Bundled Files ----------
def get_asset_path(relative_path):
    """Returns the absolute path to the asset whether running from source or PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', Path(__file__).parent)
    return Path(base_path) / relative_path

# ---------- API Key is no longer needed in this file ----------
# keys = json.loads(Path("config/keys.json").read_text())
# GROQ_API_KEY = keys["groq"]

# ---------- The request now goes to your local Node.js server ----------
MIDDLE_SERVER_URL = "https://aura-backend-6upw.onrender.com/api/detect-intent"

# ---------- Intent Detection Logic ----------
def detect_intent(user_input):
    """
    Detects intent by sending the user's input to the local server,
    which then securely calls the Groq API.
    """
    try:
        # The request body is now a simple JSON object with the user's input.
        payload = {"userInput": user_input}
        
        # The request is sent to your local server's new endpoint.
        response = requests.post(MIDDLE_SERVER_URL, json=payload)
        
        # Raise an exception for bad status codes (like 404 or 500)
        response.raise_for_status()

        # The server returns a JSON object with the intent and confidence.
        data = response.json()
        intent = data.get("intent", "unknown")
        confidence = data.get("confidence", 0.0)
        
        return intent, confidence

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error connecting to the intent detection server: {e}")
        print(f"Is the Node.js server running at http://localhost:3000 ?")
        return "error", 0.0
    except Exception as e:
        print(f"⚠️ An unexpected error occurred during intent detection: {e}")
        return "error", 0.0

# ---------- Testing ----------
if __name__ == "__main__":
    print("🤖 Intent Detector (via local server)")
    while True:
        text = input("🗣️ User: ")
        if text.lower() in ["exit", "quit"]:
            break
        intent, confidence = detect_intent(text)
        print(f"🔎 Detected Intent: {intent} (Confidence: {confidence})")
