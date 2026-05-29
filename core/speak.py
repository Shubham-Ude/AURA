import pyttsx3
from core.gui_interface import gui_interface

engine = pyttsx3.init()
engine.setProperty('rate', 190)

def speak(text):
    print(f"AURA 🟢: {text}")
    engine.say(text)
    gui_interface.display_aura_text(text)
    engine.runAndWait()

