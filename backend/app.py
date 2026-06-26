import os
import sqlite3
from flask import Flask, render_template, request, jsonify
from backend.database import DB_PATH, init_db
from backend.chatbot import get_chatbot_response, log_chat_history
from backend.symptom_checker import analyze_symptoms
from backend.medicine_info import lookup_medicine, get_autocomplete_suggestions

# Compute base and directories to map to the workspace structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, 
            template_folder=TEMPLATE_DIR, 
            static_folder=STATIC_DIR)

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 1)
        
        if not message:
            return jsonify({"error": "Message is empty"}), 400

        # Process message via chatbot NLP module
        result = get_chatbot_response(message, user_id)
        
        # Log to chat history database
        log_chat_history(user_id, message, result['response'])
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/symptom-check', methods=['POST'])
def symptom_check():
    try:
        data = request.get_json() or {}
        symptoms = data.get('symptoms', '').strip()
        
        if not symptoms:
            return jsonify({"error": "Symptoms input is empty"}), 400
            
        result = analyze_symptoms(symptoms)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health-tips', methods=['GET'])
def health_tips():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, content, category FROM HealthTips")
        rows = cursor.fetchall()
        conn.close()

        tips_by_category = {"diet": [], "exercise": [], "water": [], "sleep": []}
        for r in rows:
            cat = r[2]
            if cat in tips_by_category:
                tips_by_category[cat].append({
                    "title": r[0],
                    "content": r[1]
                })

        return jsonify(tips_by_category)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/medicine', methods=['GET'])
def medicine():
    try:
        name = request.args.get('name', '').strip()
        if not name:
            return jsonify({"error": "Medicine name parameter is required"}), 400
            
        result = lookup_medicine(name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/medicine/suggest', methods=['GET'])
def medicine_suggest():
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify([])
            
        suggestions = get_autocomplete_suggestions(query)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def chat_history():
    try:
        user_id = request.args.get('user_id', 1)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message, response, timestamp FROM ChatHistory WHERE user_id = ? ORDER BY id DESC LIMIT 50", 
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        history = []
        for r in rows:
            history.append({
                "message": r[0],
                "response": r[1],
                "timestamp": r[2]
            })
            
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history/clear', methods=['POST'])
def clear_history():
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ChatHistory WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "History cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/profile', methods=['POST'])
def update_profile():
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()

        if not name:
            return jsonify({"error": "Name is required"}), 400

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM Users WHERE id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute(
                "UPDATE Users SET name = ?, email = ? WHERE id = ?", 
                (name, email, user_id)
            )
        else:
            cursor.execute(
                "INSERT INTO Users (id, name, email) VALUES (?, ?, ?)", 
                (user_id, name, email)
            )
            
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Profile updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the server locally on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
