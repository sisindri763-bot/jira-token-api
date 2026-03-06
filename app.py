# from flask import Flask, jsonify
# import requests
# import os
# import time
# from jira import JIRA_REFRESH_TOKEN
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)

# CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
# CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")
# # REFRESH_TOKEN = os.getenv("JIRA_REFRESH_TOKEN")
# REFRESH_TOKEN=JIRA_REFRESH_TOKEN
# TOKEN_URL = "https://auth.atlassian.com/oauth/token"

# ACCESS_TOKEN = None
# TOKEN_EXPIRY = 0


# @app.route("/")
# def home():
#     return "Jira Token API running"


# @app.route("/generate-token")
# def generate_token():

#     global ACCESS_TOKEN
#     global TOKEN_EXPIRY
#     global REFRESH_TOKEN

#     # if token still valid return cached token
#     if ACCESS_TOKEN and time.time() < TOKEN_EXPIRY:
#         return jsonify({"access_token": ACCESS_TOKEN})

#     payload = {
#         "grant_type": "refresh_token",
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "refresh_token": REFRESH_TOKEN
#     }

#     headers = {
#         "Content-Type": "application/json"
#     }

#     response = requests.post(TOKEN_URL, json=payload, headers=headers)

#     data = response.json()

#     ACCESS_TOKEN = data.get("access_token")
#     REFRESH_TOKEN = data.get("refresh_token", REFRESH_TOKEN)

#     # token expires in ~1 hour
#     TOKEN_EXPIRY = time.time() + 3500

#     return jsonify({
#         "access_token": ACCESS_TOKEN
#     })


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 10000))
#     app.run(host="0.0.0.0", port=port)



from flask import Flask, jsonify
import requests
import os
import time
from dotenv import load_dotenv
import jira

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("JIRA_CLIENT_ID")
CLIENT_SECRET = os.getenv("JIRA_CLIENT_SECRET")

REFRESH_TOKEN = jira.JIRA_REFRESH_TOKEN

TOKEN_URL = "https://auth.atlassian.com/oauth/token"

ACCESS_TOKEN = None
TOKEN_EXPIRY = 0


@app.route("/")
def home():
    return "Jira Token API running"


def update_refresh_token(new_token):
    """
    Update refresh token inside jira.py file
    """
    with open("jira.py", "w") as f:
        f.write(f'JIRA_REFRESH_TOKEN = "{new_token}"\n')


@app.route("/generate-token")
def generate_token():

    global ACCESS_TOKEN
    global TOKEN_EXPIRY
    global REFRESH_TOKEN

    # return cached token if still valid
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

    if "access_token" not in data:
        return jsonify({
            "error": "Failed to generate token",
            "response": data
        })

    ACCESS_TOKEN = data.get("access_token")

    # get new refresh token from Atlassian
    new_refresh_token = data.get("refresh_token")

    if new_refresh_token:
        REFRESH_TOKEN = new_refresh_token
        update_refresh_token(new_refresh_token)

    # token expiry (~1 hour)
    TOKEN_EXPIRY = time.time() + 3500

    return jsonify({
        "access_token": ACCESS_TOKEN
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)