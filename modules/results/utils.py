from flask import Flask
import requests
from config import Config
import re
import json
from flask import session, redirect, url_for

def build_prompt(answers, timezone = None):
    lines = [
        "You are a career advisor AI.",
    ]
    if timezone:
        lines.append(f"The user's timezone is: {timezone}. Recommend universities and degrees relevant to this region.")
    lines += [
        "Based on the user's behavioral answers, recommend 3 to 5 career paths.",
        "For each career path, provide at least two or three different university course options in the user's region.",
        "For each course option, provide:",
        "- Example university in the user's region",
        "- Example degree/course name",
        "- Estimated annual fee in AUD (e.g., $35,000)",
        "Format the response as valid JSON inside ```json``` tags.Do not include the question or prompt or extra information in your output. Begin directly with the JSON.",
        "Example JSON format:",
       '''
        ```json
        [
            {
                "careerPath": "Career Name",
                "courseOptions": [
                {
                    "university": "University Name",
                    "courseName": "Degree/Course Name",
                    "annualFee": "$35,000"
                }
                // ...at least two or three course options
                ]
            }
            // ...3 to 5 career objects
        ]
        ```
        '''
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
    response = requests.post(Config.MODEL_ENDPOINT, headers=headers, json={"inputs": prompt, "parameters": { "return_full_text": False }})
    response.raise_for_status()

    result = response.json()
    text = result[0].get("generated_text", "")

    print("🔍 Raw LLM output:\n", text)

    json = extract_json(text)
    
    return {"json": json, "output": text}


def extract_json(text):
    json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        try:
            parsed_json = json.loads(json_str)
            print(json.dumps(parsed_json, indent=2))  # Pretty-print JSON
            return parsed_json
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No JSON content found in response.")
        return None