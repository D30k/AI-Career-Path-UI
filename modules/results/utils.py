from flask import Flask
import requests
from config import Config
import re
from flask import session, redirect, url_for

def build_prompt(answers, timezone = None):
    lines = [
        "You are a career advisor AI.",
    ]
    if timezone:
        lines.append(f"The user's timezone is: {timezone}. Recommend universities and degrees relevant to this region.")
    lines += [
        "Based on the user's behavioral answers, recommend 3 to 5 career paths.",
        "For each career path, provide at least two or three different university course options.",
        "For each course option, provide:",
        "- Example university in the user's region",
        "- Example degree/course name",
        "- Estimated annual fee in AUD (e.g., $35,000)",
        "Format each recommendation like:",
        "- Career: Data Scientist",
        "  1. University: Swinburne University | Course: Bachelor of Data Science | Fee: $35,000",
        "  2. University: Monash University | Course: Bachelor of Computer Science | Fee: $36,000",
        "  3. University: University of Melbourne | Course: Bachelor of Science (Data Science) | Fee: $38,000",
        "Add no extra explanation. Begin directly with the list. provide career and university data in json format",
        "",
        "User's behavioral answers:"
    ]
    for qa in answers:
        lines.append(f"- {qa["question"]}: {qa["answer"]}")
    return "\n".join(lines)     


def query_mistral(prompt):
    headers = {
        "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    user_id = session.get('user_id')
    email = session.get('email')
    country = session.get('country')
    age = session.get('age')
    gender = session.get('gender')
    highest_education = session.get('highest_education')

# Create a comma-separated string of user info
    user_info_str = f"User: {email}, Country: {country}, Age: {age}, Gender: {gender}, Education: {highest_education}"

    
    response = requests.post(Config.MODEL_ENDPOINT, headers=headers, json={"inputs": prompt, "user_info": user_info_str})
    response.raise_for_status()

    result = response.json()
    text = result[0].get("generated_text", "")

    print("🔍 Raw LLM output:\n", text)

    # Updated regex
    pattern = r"-\s*(.*?):\s*(\d{1,3})% match"
    matches = re.findall(pattern, text, re.IGNORECASE)
    print("🧪 Matches found:", matches)

    structured = [{"career": name.strip(), "match": int(percent)} for name, percent in matches]
    return {"recommendations": structured, "output": text}