from flask import Flask, render_template, request, jsonify
import requests
import os
import re
import sqlite3
from config import Config

from flask import session, redirect, url_for

from modules.auth.routes import auth
from modules.quiz.routes import quiz
from modules.results.routes import results


app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY


app.register_blueprint(auth)
app.register_blueprint(quiz)
app.register_blueprint(results)

# ------------------ START APP ------------------ #

if __name__ == '__main__':
    app.run(debug=True)
