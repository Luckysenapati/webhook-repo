# from flask import Flask, request, jsonify, abort
# from pymongo import MongoClient
# from datetime import datetime
# import logging
# import hmac
# import hashlib
# import os

# app = Flask(__name__)

# # MongoDB setup
# client = MongoClient("mongodb://localhost:27017/")
# db = client["github_actions"]
# collection = db["events"]

# # Logging setup
# logging.basicConfig(level=logging.INFO)

# # Optional: GitHub secret (set this in GitHub webhook settings and as an environment variable)
# GITHUB_SECRET = os.getenv("GITHUB_SECRET", "")  # Set this securely!

# # Utility to verify GitHub webhook signatures
# def verify_signature(payload, signature):
#     if not GITHUB_SECRET:
#         return True  # Signature checking disabled if no secret
#     mac = hmac.new(GITHUB_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
#     expected_signature = 'sha256=' + mac.hexdigest()
#     return hmac.compare_digest(expected_signature, signature)

# @app.route("/")
# def index():
#     return "✅ GitHub Webhook Listener is running!"

# @app.route("/webhook", methods=["POST"])
# def webhook():
#     raw_data = request.data
#     signature = request.headers.get("X-Hub-Signature-256", "")

#     # Verify signature (optional)
#     if not verify_signature(raw_data, signature):
#         logging.warning("❌ Signature verification failed.")
#         abort(403, "Invalid signature")

#     data = request.get_json(force=True)
#     logging.info(f"📦 Received webhook data: {data}")

#     payload = {}

#     # Handle push event
#     if "pusher" in data:
#         payload = {
#             "request_id": data.get("after"),
#             "author": data.get("pusher", {}).get("name"),
#             "action": "PUSH",
#             "from_branch": data.get("ref", "").split("/")[-1],
#             "to_branch": data.get("ref", "").split("/")[-1],
#             "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
#         }

#     # Handle pull request event
#     elif "pull_request" in data:
#         action = "MERGE" if data.get("action") == "closed" and data["pull_request"].get("merged") else "PULL_REQUEST"
#         payload = {
#             "request_id": str(data["pull_request"].get("id")),
#             "author": data.get("sender", {}).get("login"),
#             "action": action,
#             "from_branch": data["pull_request"]["head"].get("ref"),
#             "to_branch": data["pull_request"]["base"].get("ref"),
#             "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
#         }

#     # Save and respond
#     if payload:
#         collection.insert_one(payload)
#         logging.info(f"✅ Event saved: {payload}")
#         return jsonify({"status": "saved", "data": payload}), 200

#     logging.warning("⚠️ Invalid data received.")
#     return jsonify({"error": "invalid data"}), 400

# @app.route("/events", methods=["GET"])
# def get_events():
#     data = list(collection.find({}, {"_id": 0}))
#     return jsonify(data)

# if __name__ == "__main__":
#     app.run(port=5000)








from flask import Flask
from routes import webhook  # Import the Blueprint

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(webhook)

@app.route("/")
def index():
    return "✅ GitHub Webhook Listener is running!"

if __name__ == "__main__":
    app.run(port=5000)
