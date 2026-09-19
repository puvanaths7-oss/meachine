import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from chatbot_config import CHATBOT_TITLE, MODEL_NAME, SYSTEM_PROMPT

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


def get_client():
    global client, api_key
    current_key = os.getenv("GEMINI_API_KEY")
    if not current_key:
        load_dotenv(override=True)
        current_key = os.getenv("GEMINI_API_KEY")

    if current_key and (client is None or current_key != api_key):
        api_key = current_key
        client = genai.Client(api_key=api_key)

    return client


@app.route("/")
def index():
    return render_template("index.html", chatbot_title=CHATBOT_TITLE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Please enter a question."}), 400

    active_client = get_client()
    if not active_client:
        return jsonify({"error": "GEMINI_API_KEY is not configured in the .env file."}), 500

    try:
        response = active_client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        answer = (response.text or "").strip()
        return jsonify({
            "response": answer or "I could not generate a response. Please try again."
        })

    except Exception as exc:
        return jsonify({"error": f"Gemini API error: {str(exc)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
