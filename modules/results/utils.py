from flask import Flask
import requests
from config import Config

from flask import session, redirect, url_for

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


def query_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(Config.MODEL_ENDPOINT, headers=headers, json={"inputs": prompt})
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
