from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')

# Directly set your Hugging Face API key
HUGGINGFACE_API_KEY = "*"
MISTRAL_ENDPOINT = 'https://api-inference.huggingface.co/models/mistralai/Mistral-8x7B-Instruct-v0.1'

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Serve the quiz page
@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# Endpoint to receive quiz answers and query LLM
@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    data = request.json or {}
    answers = data.get('answers', {})
    if not answers:
        return jsonify({'error': 'No answers provided'}), 400

    # Build prompt for Mistral
    prompt = build_prompt(answers)

    # Query the Mistral model
    try:
        ai_text = query_mistral(prompt)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Return the AI-generated recommendation
    return jsonify({'result': ai_text})

# Construct the prompt based on user answers
def build_prompt(answers: dict) -> str:
    lines = ['The following are behavioral answers from a student:']
    for question, answer in answers.items():
        lines.append(f"- {question}: \"{answer}\"")
    lines.append('')
    lines.append('Based on these preferences, suggest 3 suitable career paths, 3 professional goals, and 3 universities worldwide where this student would thrive. Provide detailed explanations for each.')
    return '\n'.join(lines)

# Call Hugging Face inference API
def query_mistral(prompt: str) -> str:
    headers = {
        'Authorization': f'Bearer {HUGGINGFACE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {'inputs': prompt}
    response = requests.post(MISTRAL_ENDPOINT, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    output = response.json()
    # Extract generated text
    if isinstance(output, list) and 'generated_text' in output[0]:
        return output[0]['generated_text']
    return output.get('generated_text', str(output))

if __name__ == '__main__':
    app.run(debug=True)
