from flask import Flask
from config import Config

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
