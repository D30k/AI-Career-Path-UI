from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
import os
from dotenv import load_dotenv
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['email'] = user[1]
            return redirect(url_for('quiz.home'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = generate_password_hash(password)
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
            conn.commit()
            conn.close()
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="Email already exists")
    return render_template('register.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('quiz.home'))
