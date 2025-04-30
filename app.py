from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import sqlite3
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function




# Load environment variables (Hugging Face API key)
load_dotenv()


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_dev_key")

# Hugging Face configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ENDPOINT = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"




# ------------------ ROUTES ------------------ #

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('index.html')  # User is logged in
    else:
        return redirect(url_for('login'))     # Force login first


@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')


@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    data = request.json
    answers = data.get("answers", {})
    if not answers:
        return jsonify({"error": "No answers received."}), 400

    prompt = build_prompt(answers)
    try:
        result = query_mistral(prompt)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/follow-up', methods=['POST'])
def follow_up():
    data = request.json
    question = data.get("followup", "").strip()
    if not question:
        return jsonify({"error": "No question received"}), 400

    prompt = f"You are a career guidance expert AI. Answer the user's follow-up question below.\n\nQuestion: \"{question}\"\n\nGive a thoughtful and helpful response."
    try:
        result = query_mistral(prompt)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['email'] = user[1]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Email already exists")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ------------------ HELPERS ------------------ #

def build_prompt(answers):
    lines = [
        "You are a career advisor AI.",
        "Based on the user's behavioral answers, recommend 3 to 5 career paths with a confidence percentage (e.g., 87%) for each.",
        "Format each career on a new line like:",
        "- Career Name: 87% match",
        "Add no extra explanation. Begin directly with the list.",
        "",
        "User's behavioral answers:"
    ]
    for question, answer in answers.items():
        lines.append(f"- {question}: {answer}")
    return "\n".join(lines)


import re

def query_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(MODEL_ENDPOINT, headers=headers, json={"inputs": prompt})
    response.raise_for_status()

    result = response.json()
    text = result[0].get("generated_text", "")

    print("🔍 Raw LLM output:\n", text)

    # Updated regex
    pattern = r"-\s*(.*?):\s*(\d{1,3})% match"
    matches = re.findall(pattern, text, re.IGNORECASE)
    print("🧪 Matches found:", matches)

    structured = [{"career": name.strip(), "match": int(percent)} for name, percent in matches]
    return {"recommendations": structured}




# ------------------ START APP ------------------ #

if __name__ == '__main__':
    app.run(debug=True)
