from flask import Blueprint, session, render_template, request, jsonify, url_for

from modules.results.utils import build_prompt, query_mistral

results = Blueprint('results', __name__)

@results.route('/submit-quiz', methods=['POST'])
def submit_quiz():
      
    data = request.json
    answers = data.get("answers", {})
    timezone = data.get("timezone", None)
    
    if not answers:
        return jsonify({"error": "No answer received"}), 400
    
     # Add a random value to the prompt to encourage new generations
    session['answers'] = answers
    session['timezone'] = timezone
    prompt = build_prompt(answers, timezone)
    try:
        result = query_mistral(prompt)
        session['result'] = result
        return jsonify({"redirect": url_for('results.result')})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@results.route('/follow-up', methods=['POST'])
def follow_up():
    data = request.json
    question = data.get("followup", "").strip()
    if not question:
        return jsonify({"error": "No question received"}), 400

    prompt = (
        f"You are a career guidance expert AI. Answer the user's follow-up question below.\n\n"
        f"Question: \"{question}\"\n\n"
        "Give a thoughtful and helpful response. Answer should begin inside ```json``` tags. "
        "Example JSON format:\n```json\n{\n\"answer\": \"Your answer here\"\n}\n```:\n"
        )
   
   
    try:
        result = query_mistral(prompt)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@results.route('/result')
def result():

    result = session.get('result', [])
    return render_template('result.html', result=result)  
