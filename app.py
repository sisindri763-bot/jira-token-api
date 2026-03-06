from flask import Flask, jsonify
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("JIRA_REFRESH_TOKEN")

TOKEN_URL = "https://auth.atlassian.com/oauth/token"

ACCESS_TOKEN = None
TOKEN_EXPIRY = 0


@app.route("/")
def home():
    return "Jira Token API running"


@app.route("/generate-token")
def generate_token():

    global ACCESS_TOKEN
    global TOKEN_EXPIRY
    global REFRESH_TOKEN

    # if token still valid return cached token
    if ACCESS_TOKEN and time.time() < TOKEN_EXPIRY:
        return jsonify({"access_token": ACCESS_TOKEN})

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

    ACCESS_TOKEN = data.get("access_token")
    REFRESH_TOKEN = data.get("refresh_token", REFRESH_TOKEN)

    # token expires in ~1 hour
    TOKEN_EXPIRY = time.time() + 3500

    return jsonify({
        "access_token": ACCESS_TOKEN
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)