from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv, set_key

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("JIRA_REFRESH_TOKEN")

TOKEN_URL = "https://auth.atlassian.com/oauth/token"
ENV_FILE = ".env"


# ---------------- HOME ROUTE ----------------
@app.route("/")
def home():
    return "Jira Token API is running"


# ---------------- GENERATE TOKEN ----------------
@app.route("/generate-token")
def generate_token():

    global REFRESH_TOKEN

    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(TOKEN_URL, json=payload, headers=headers)

    data = response.json()

    access_token = data.get("access_token")
    new_refresh_token = data.get("refresh_token")

    # Atlassian rotates refresh tokens
    if new_refresh_token:
        REFRESH_TOKEN = new_refresh_token
        set_key(ENV_FILE, "JIRA_REFRESH_TOKEN", new_refresh_token)

    return jsonify({
        "access_token": access_token
    })


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(port=4000, debug=True)