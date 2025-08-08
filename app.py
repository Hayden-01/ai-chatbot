from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Replace this with your company's details before selling
COMPANY_NAME = "Your Company Name"
WELCOME_MESSAGE = f"Welcome to {COMPANY_NAME} customer service AI!"

# Simple chatbot logic
def chatbot_response(user_input):
    user_input = user_input.lower()
    if "hello" in user_input:
        return f"Hello! Thanks for contacting {COMPANY_NAME}. How can I help you today?"
    elif "help" in user_input:
        return "Sure, please tell me more about your issue."
    elif "hours" in user_input:
        return f"{COMPANY_NAME} is open 9am - 5pm, Monday to Friday."
    elif "bye" in user_input:
        return "Goodbye! Have a great day."
    else:
        return "I'm not sure about that. Could you please rephrase?"

# Routes
@app.route("/")
def home():
    return render_template("index.html", company_name=COMPANY_NAME, welcome_message=WELCOME_MESSAGE)

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_message = request.json.get("message", "")
    bot_reply = chatbot_response(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    # Use dynamic port for Render, default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "1") == "1"

    app.run(host="0.0.0.0", port=port, debug=debug_mode)
