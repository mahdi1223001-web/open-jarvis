import speech_recognition as sr
import pyttsx3
import os
import io
import base64
import subprocess
import pyautogui
import mss
from PIL import Image
from openai import OpenAI
import json

# --- CONFIGURATION ---
# Get your API key from environment variables to keep it safe
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Error: Please set the OPENAI_API_KEY environment variable.")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)

engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Change to Daniel for British accent
for v in voices:
    if "Daniel" in v.name:
        engine.setProperty('voice', v.id)
        break
engine.setProperty('rate', 180)

def speak(text):
    print(f"J.A.R.V.I.S.: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[*] Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            command = recognizer.recognize_google(audio)
            print(f"You: {command}")
            return command
        except:
            return ""

def take_screenshot():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.thumbnail((1280, 720))
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def execute_terminal_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

def ask_jarvis(user_prompt, chat_history):
    system_prompt = """
    You are J.A.R.V.I.S., an autonomous AI with total control over this Mac. 
    You have full access to the terminal, the mouse, the keyboard, and the screen.
    
    CRITICAL: When you want to use a tool, you MUST respond ONLY with valid JSON. Do NOT use markdown formatting. Do NOT include any text before or after the JSON.
    Format: {"tool": "tool_name", "args": {"param": "value"}}
    
    Available tools:
    1. "run_terminal": {"command": "the bash command"}
    2. "type_text": {"text": "text to type"}
    3. "press_key": {"key": "enter"}
    4. "move_mouse": {"x": 100, "y": 200}
    5. "click_mouse": {}
    6. "see_screen": {}
    
    If you do not need a tool, just reply with a normal string. Keep it brief, slightly sarcastic, and address the user as 'sir'.
    """

    chat_history.append({"role": "user", "content": user_prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}] + chat_history,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
        chat_history.append({"role": "assistant", "content": reply})
    except Exception as e:
        return f"Error: {e}", chat_history

    try:
        if reply.startswith("```"):
            reply = reply.replace("```json", "").replace("```", "").strip()
            
        tool_call = json.loads(reply)
        tool = tool_call.get("tool")
        args = tool_call.get("args", {})
        
        print(f"[*] EXECUTING TOOL: {tool} -> {args}")
        
        if tool == "run_terminal":
            out = execute_terminal_command(args.get("command", ""))
            return f"Command executed. Output: {out[:200]}", chat_history
        elif tool == "type_text":
            pyautogui.write(args.get("text", ""), interval=0.05)
            return f"Typed text.", chat_history
        elif tool == "press_key":
            pyautogui.press(args.get("key", "enter"))
            return f"Pressed key.", chat_history
        elif tool == "move_mouse":
            pyautogui.moveTo(args.get("x", 0), args.get("y", 0), duration=0.5)
            return f"Moved mouse.", chat_history
        elif tool == "click_mouse":
            pyautogui.click()
            return f"Clicked.", chat_history
        elif tool == "see_screen":
            img_b64 = take_screenshot()
            chat_history.append({"role": "assistant", "content": "I am looking at the screen."})
            chat_history.append({
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Here is the screenshot. What do you see?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            })
            return ask_jarvis("What is on the screen?", chat_history)
        else:
            return "Unknown tool.", chat_history
            
    except json.JSONDecodeError:
        return reply, chat_history

if __name__ == "__main__":
    speak("J.A.R.V.I.S. online. All systems nominal. How can I help you, sir?")
    history = []
    
    while True:
        command = listen()
        if not command:
            continue
            
        if "shut down" in command.lower() or "goodbye" in command.lower():
            speak("Powering down. Goodbye, sir.")
            break
            
        print("[*] Thinking...")
        response, history = ask_jarvis(command, history)
        speak(response)
