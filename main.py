import sys
import threading
from core.listen import listen
from core.speak import speak
from core.genai import aura_brain
from core.executor import execute

# GUI setup
try:
    from core.gui_interface import gui_interface
    from aura_ui import launch_gui  # 👈 Import GUI launcher
    GUI_ENABLED = True
except ImportError:
    gui_interface = None
    GUI_ENABLED = False

DEBUG_MODE = "--debug" in sys.argv

def start():
    if DEBUG_MODE:
        print("🔵 AURA CLI Debug Mode Activated")
    else:
        speak("AURA is ready. Listening for your command...")

    while True:
        if DEBUG_MODE:
            command = input("\n🗣️ User (CLI): ")
        else:
            command = listen()

        if not command:
            error_msg = "I didn’t catch that. Please repeat."
            if DEBUG_MODE:
                print(error_msg)
            else:
                speak(error_msg)
            continue

        if "exit" in command.lower() or "shutdown" in command.lower():
            exit_msg = "Shutting down. See you soon."
            if DEBUG_MODE:
                print(exit_msg)
            else:
                speak(exit_msg)
            break

        if GUI_ENABLED:
            gui_interface.display_user_text(command)

        # Process command
        response = aura_brain(command)
        command_to_execute = response.get("command", "")
        description = response.get("description", "")

        print("\n🧠 AURA Response:", response)

        if command_to_execute:
            execute(command_to_execute, description)
        else:
            if DEBUG_MODE:
                print(f"🤖 AURA: {description or 'I couldn’t process that command.'}")
            else:
                speak(description or "I couldn’t process that command.")

        if GUI_ENABLED:
            gui_interface.display_aura_text(description)

if __name__ == "__main__":
    if GUI_ENABLED:
        # 👇 Launch GUI in a background thread
        gui_thread = threading.Thread(target=launch_gui, daemon=True)
        gui_thread.start()

    start()
