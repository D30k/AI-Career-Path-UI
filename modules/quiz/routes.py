from flask import Blueprint, Flask, render_template 

from modules.auth.utils import login_required

quiz = Blueprint('quiz', __name__)

@quiz.route('/')
@login_required
def home():
    return render_template('index.html')  

@quiz.route('/quiz')
@login_required
def quizzes():
    return render_template('quiz.html')

