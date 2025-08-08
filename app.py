from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# In-memory database for trial users
DATABASE = "users.db"

# Company settings
COMPANY_NAME = "Your Company Name"
FREE_TRIAL_DAYS = 7

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        email TEXT PRIMARY KEY,
                        start_date TEXT,
                        active INTEGER DEFAULT 1
                    )''')
        conn.commit()

init_db()

def is_trial_valid(email):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT start_date, active FROM users WHERE email=?", (email,))
        row = c.fetchone()
        if not row:
            return False
        start_date = datetime.strptime(row[0], "%Y-%m-%d")
        active = row[1]
        return active == 1 and datetime.now() < start_date + timedelta(days=FREE_TRIAL_DAYS)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            with sqlite3.connect(DATABASE) as conn:
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO users (email, start_date) VALUES (?, ?)", 
                          (email, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
            return redirect(url_for("chat", email=email))
    return render_template("index.html", company=COMPANY_NAME)

@app.route("/chat/<email>")
def chat(email):
    if not is_trial_valid(email):
        return redirect(url_for("expired"))
    return render_template("chat.html", company=COMPANY_NAME, email=email)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    user_input = data.get("message", "")
    email = data.get("email", "")
    if not is_trial_valid(email):
        return jsonify({"reply": "Your free trial has expired. Please subscribe to continue."})

    headers = {
        "Authorization": "Bearer YOUR_OPENROUTER_KEY",
        "HTTP-Referer": "https://yourdomain.com",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral",
        "messages": [{"role": "user", "content": user_input}]
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        reply = r.json()['choices'][0]['message']['content']
    except:
        reply = "Sorry, I couldn't fetch a response. Try again later."
    return jsonify({"reply": reply})

@app.route("/expired")
def expired():
    return render_template("expired.html", company=COMPANY_NAME)