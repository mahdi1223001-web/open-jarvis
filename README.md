# Open-J.A.R.V.I.S. 🤖

An autonomous, voice-controlled AI agent for macOS. 

## What it does
Open-J.A.R.V.I.S. is an open-source project that uses OpenAI's GPT-4o model to "see" your screen, move your mouse, type text, and run terminal commands based on voice instructions. It transforms your Mac into an interactive AI environment.

## Features
- **Vision:** Takes native screenshots and uses GPT-4o's vision capabilities to analyze the UI and react to what is happening on the screen.
- **Tool Calling:** Automatically executes Python scripts and terminal commands based on natural language instructions.
- **Voice Control:** Uses `SpeechRecognition` for live audio input and `pyttsx3` for high-quality speech output (supports British accents for that authentic J.A.R.V.I.S. feel).
- **Total OS Control:** Can open apps, search the web, manage files, and simulate human mouse and keyboard behavior via `pyautogui`.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/mahdi1223001-web/open-jarvis.git
   cd open-jarvis
