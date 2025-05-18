from flask import Blueprint, Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask import session, redirect, url_for

from modules.results.utils import build_prompt, query_mistral

results = Blueprint('results', __name__)

@results.route('/submit-quiz', methods=['POST'])
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


import re

@results.route('/follow-up', methods=['POST'])
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


