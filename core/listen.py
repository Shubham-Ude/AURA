import speech_recognition as sr
from core.gui_interface import gui_interface

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎧 AURA is listening... speak clearly.")
        
        # Adjust for ambient noise (noise suppression)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen with time constraints
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
            print("🔍 Recognizing...")
            command = recognizer.recognize_google(audio)
            gui_interface.display_user_text(command)
            print(f"🗣️ You said: {command}")
            return command.lower()

        except sr.WaitTimeoutError:
            print("⚠️ Timeout: No voice detected.")
            return ""

        except sr.UnknownValueError:
            print("❌ Speech not recognized.")
            return ""

        except sr.RequestError as e:
            print(f"🔌 API Error: {e}")
            return ""
