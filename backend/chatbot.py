import os
import re
import sqlite3
import urllib.request
import urllib.error
import json
from backend.database import DB_PATH

# Permanent System Prompt
SYSTEM_PROMPT = """You are a caring AI Healthcare Assistant.

Your personality:
- Friendly
- Caring
- Empathetic
- Calm
- Professional
- Encouraging

You should:
- Speak naturally
- Ask follow-up questions
- Understand user context
- Remember previous messages
- Explain medical concepts simply
- Suggest healthy habits
- Be conversational

You should NOT:
- Give definitive diagnoses
- Prescribe medications
- Claim certainty about diseases
- Replace professional healthcare advice

For emergencies such as:
Chest pain
Breathing difficulty
Stroke symptoms
Severe bleeding
Immediately advise seeking emergency medical care.

Always sound like a supportive healthcare companion."""

# Custom Env Loader to load .env variables manually
def load_env():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception as e:
            print("Error loading .env file:", e)

# Run environment loader on file import
load_env()

def get_chat_history_for_groq(user_id, limit=6):
    """
    Fetch the last `limit` messages/responses chronologically from SQLite to pass to Llama memory context.
    """
    history = []
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message, response FROM ChatHistory WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        # Reverse rows to return them in ascending chronological order
        for msg, resp in reversed(rows):
            history.append({"role": "user", "content": msg})
            history.append({"role": "assistant", "content": resp})
    except Exception as e:
        print("Database query history error:", e)
    return history

def get_chatbot_response(user_message, user_id=1):
    if not user_message:
        return {
            "response": "Please enter a message.",
            "intent": "empty",
            "animation": "idle",
            "emergency": False
        }

    msg = user_message.lower().strip()

    # 1. Emergency keywords check
    emergency_keywords = ["chest pain", "breathing difficulty", "severe bleeding", "stroke symptoms", "heart attack", "stroke", "difficulty breathing", "heavy bleeding"]
    is_emergency_precheck = any(kw in msg for kw in emergency_keywords)

    # 2. Retrieve history and append system instructions
    history_messages = get_chat_history_for_groq(user_id, limit=5) # retrieve last 5 pairs of messages
    
    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages_payload.extend(history_messages)
    messages_payload.append({"role": "user", "content": user_message})

    # 3. Query GROQ API
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        warning_msg = (
            "⚠️ **System Alert:** `GROQ_API_KEY` is missing from the environment.\n\n"
            "Please create a `.env` file in your root workspace containing:\n"
            "```env\n"
            "GROQ_API_KEY=your_groq_api_key\n"
            "```\n"
            "Once saved, restart the Flask server to load the key."
        )
        return {
            "response": warning_msg,
            "intent": "system_warning",
            "animation": "concern",
            "emergency": False
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages_payload,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            res_data = response.read().decode('utf-8')
            res_json = json.loads(res_data)
            response_text = res_json['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        response_text = f"⚠️ **GROQ API Error:** Received status code {e.code}. Details: {err_body}"
    except Exception as e:
        response_text = f"⚠️ **Connection Failure:** Failed to connect to GROQ server. Detail: {str(e)}"

    # 4. Generate Metadata Heuristics
    emergency = is_emergency_precheck or any(kw in response_text.lower() for kw in emergency_keywords)
    
    # Intent heuristics
    intent = "fallback"
    if emergency:
        intent = "emergency"
    elif any(kw in msg for kw in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]):
        intent = "greeting"
    elif any(kw in msg for kw in ["diet", "nutrition", "eat", "food"]):
        intent = "diet_tips"
    elif any(kw in msg for kw in ["exercise", "workout", "fitness", "active"]):
        intent = "exercise_tips"
    elif any(kw in msg for kw in ["water", "hydrate", "hydration", "drink"]):
        intent = "water_tips"
    elif any(kw in msg for kw in ["sleep", "insomnia", "bedtime", "rest"]):
        intent = "sleep_tips"
    elif any(kw in msg for kw in ["fever", "headache", "cough", "pain", "sore throat", "nausea"]):
        intent = "symptom_check"
    elif any(kw in msg for kw in ["paracetamol", "ibuprofen", "metformin", "dolo", "crocin", "saridon", "combiflam", "azithral"]):
        intent = "medicine"

    # Avatar expression heuristics
    animation = "nod"
    if emergency:
        animation = "concern"
    elif intent == "greeting":
        animation = "wave"
    elif any(kw in msg for kw in ["thank you", "thanks", "bye", "goodbye"]):
        animation = "wave"

    return {
        "response": response_text,
        "intent": intent,
        "animation": animation,
        "emergency": emergency
    }

def log_chat_history(user_id, message, response):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ChatHistory (user_id, message, response) VALUES (?, ?, ?)", 
            (user_id, message, response)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Failed to log chat history:", e)

