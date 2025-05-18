from flask import Blueprint, session, render_template, request, jsonify, url_for

from modules.results.utils import build_prompt, query_mistral

results = Blueprint('results', __name__)

@results.route('/submit-quiz', methods=['POST'])
def submit_quiz():
      
    data = request.json
    answers = data.get("answers", {})
    
    if not answers:
        return jsonify({"error": "No answer received"}), 400
    
    prompt = build_prompt(answers)
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

    prompt = f"You are a career guidance expert AI. Answer the user's follow-up question below.\n\nQuestion: \"{question}\"\n\nGive a thoughtful and helpful response."
    try:
        result = query_mistral(prompt)
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@results.route('/result')
def result():
    result = session.get('result', [])
    return render_template('result.html', result=result)  
