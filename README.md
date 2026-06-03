# 🤖 AURA — AI-Powered Voice Assistant

> **A.U.R.A.** is a Windows-based AI voice assistant with a sleek, animated HUD overlay. It listens to your voice commands, processes them through a generative AI brain, and executes system actions — all while displaying a futuristic on-screen interface.

---

## ✨ Features

- 🎙️ **Voice Recognition** — Listens for natural language commands using your microphone
- 🔊 **Text-to-Speech** — Responds in a natural voice via `pyttsx3`
- 🧠 **AI Brain** — Processes commands intelligently through a GenAI model (`core/genai.py`)
- ⚙️ **System Command Execution** — Executes Windows system actions using NirCmd
- 🖥️ **Animated HUD Overlay** — A transparent, always-on-top PyQt5 widget with orbital animation and status display
- 🧵 **Threaded Architecture** — GUI and assistant run concurrently without blocking each other
- 🐛 **CLI Debug Mode** — Test commands from the terminal without a microphone
- 🧠 **Memory Module** — Persistent memory support across sessions
- ⚙️ **Configurable** — Adjustable settings via the `config/` directory

---

## 📁 Project Structure

```
AURA/
├── main.py              # Entry point — orchestrates listen → think → speak → execute loop
├── aura_ui.py           # PyQt5 HUD overlay (animated, frameless, always-on-top)
├── core/
│   ├── listen.py        # Microphone input via SpeechRecognition
│   ├── speak.py         # Text-to-speech via pyttsx3
│   ├── genai.py         # AI brain — interprets commands and generates responses
│   ├── executor.py      # Executes system commands (uses NirCmd)
│   └── gui_interface.py # Bridge between core logic and the HUD
├── memory/              # Stores context or conversation history
├── config/              # Configuration files
├── assets/
│   └── aura_bg.png      # Background image for the HUD
├── nircmd.exe           # NirCmd — Windows utility for system commands
├── nircmdc.exe          # NirCmd console variant
├── requirements.txt     # Python dependencies
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Windows OS** (required — uses NirCmd and Windows APIs)
- **Python 3.10+**
- A working **microphone**

### 1. Clone the Repository

```bash
git clone https://github.com/Shubham-Ude/AURA.git
cd AURA
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `PyAudio` may require a pre-built wheel on some Windows setups. If the install fails, try:
> ```bash
> pip install pipwin
> pipwin install pyaudio
> ```

### 3. Configure Your API Key

AURA uses a generative AI model in `core/genai.py`. Open the file and add your API key (e.g., Google Gemini or OpenAI) as instructed in the configuration section.

### 4. Run AURA

**Normal mode** (voice + GUI):
```bash
python main.py
```

**Debug / CLI mode** (type commands instead of speaking):
```bash
python main.py --debug
```

---

## 🖥️ HUD Overview

The AURA HUD is a frameless, transparent overlay that sits in the **top-right corner** of your screen. It features:

- A pulsing orbital animation (~60 FPS)
- Rotating character ring display
- Live status text showing your last command and AURA's response
- Draggable — click and drag to reposition it anywhere on screen

---

## 🔄 How It Works

```
User speaks
    ↓
core/listen.py   →  Captures audio & converts to text
    ↓
core/genai.py    →  Sends text to AI model, returns { command, description }
    ↓
core/executor.py →  Runs the system command (if any) via NirCmd
    ↓
core/speak.py    →  Speaks the description back to the user
    ↓
aura_ui.py       →  Updates HUD with user input & AURA's response
```

---

## 📦 Dependencies

| Package | Purpose |
|--------|---------|
| `SpeechRecognition` | Converts microphone audio to text |
| `PyAudio` | Audio input stream |
| `pyttsx3` | Offline text-to-speech |
| `PyQt5` | Animated HUD overlay |
| `pywin32` / `comtypes` | Windows system integration |
| `requests` | HTTP calls to AI APIs |
| `audioop-lts` | Audio processing compatibility |

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🛠️ NirCmd

AURA bundles [NirCmd](https://www.nirsoft.net/utils/nircmd.html) (`nircmd.exe` and `nircmdc.exe`) for Windows system-level commands such as controlling volume, display, or running scripts. No separate installation is needed.

---

## 🧪 Debug Mode

Use `--debug` to skip the microphone and type commands directly in the terminal — useful for testing AI responses and system commands without audio hardware:

```bash
python main.py --debug
```

```
🔵 AURA CLI Debug Mode Activated
🗣️ User (CLI): open calculator
🧠 AURA Response: {'command': 'calc', 'description': 'Opening Calculator...'}
```

---

## 🗺️ Roadmap

- [ ] Web search integration
- [ ] Custom wake word support
- [ ] More system action commands
- [ ] Conversation history & context awareness
- [ ] Cross-platform support (Linux/macOS)
- [ ] Packaged executable (`.exe`) via PyInstaller

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source. See the repository for license details.

---

## 👤 Author

**Shubham Ude**
- GitHub: [@Shubham-Ude](https://github.com/Shubham-Ude)

---

> *"AURA is ready. Listening for your command..."*
