from flask import Blueprint, Flask, render_template 

from modules.auth.utils import login_required

quiz = Blueprint('quiz', __name__)

@quiz.route('/')
def home():
    return render_template('index.html')  

@quiz.route('/quiz')
def quizzes():
    return render_template('quiz.html')

