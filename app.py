from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import sqlite3
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from flask import session, redirect, url_for

from modules.auth.utils import login_required
from modules.auth.routes import auth

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
        return redirect(url_for('auth.login'))     # Force login first


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


app.register_blueprint(auth)


# ------------------ START APP ------------------ #

if __name__ == '__main__':
    app.run(debug=True)
