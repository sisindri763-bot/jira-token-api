from flask import Flask, jsonify
import os
import requests
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

TOKEN_URL = "https://auth.atlassian.com/oauth/token"


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def get_access_token():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT refresh_token, access_token, expiry FROM jira_tokens WHERE id=1"
    )
    row = cur.fetchone()

    if row:
        refresh_token, access_token, expiry = row
    else:
        refresh_token = REFRESH_TOKEN
        access_token = None
        expiry = 0

    current_time = int(time.time())

    # Add 60 sec safety buffer
    if access_token and expiry and current_time < (expiry - 60):
        cur.close()
        conn.close()
        return access_token

    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(TOKEN_URL, json=payload, headers=headers)
    data = response.json()

    print("ATLASSIAN RESPONSE:", data)

    if "access_token" not in data:
        cur.close()
        conn.close()
        raise Exception(f"Token refresh failed: {data}")

    new_access_token = data["access_token"]
    new_refresh_token = data.get("refresh_token", refresh_token)

    expiry_time = current_time + data.get("expires_in", 3600)

    cur.execute("""
        INSERT INTO jira_tokens (id, refresh_token, access_token, expiry)
        VALUES (1,%s,%s,%s)
        ON CONFLICT (id)
        DO UPDATE SET
            refresh_token = EXCLUDED.refresh_token,
            access_token = EXCLUDED.access_token,
            expiry = EXCLUDED.expiry
    """, (new_refresh_token, new_access_token, expiry_time))

    conn.commit()
    cur.close()
    conn.close()

    return new_access_token


@app.route("/")
def home():
    return "Jira Token API running"


@app.route("/generate-token")
def generate_token():
    try:
        token = get_access_token()
        return jsonify({"access_token": token})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)