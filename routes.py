from flask import Blueprint, request, jsonify, abort
from pymongo import MongoClient
from datetime import datetime
import logging
import hmac
import hashlib
import os

# Create a Blueprint
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["github_actions"]
collection = db["events"]

# GitHub secret (set this as an env variable if needed)
GITHUB_SECRET = os.getenv("GITHUB_SECRET", "")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Signature verification
def verify_signature(payload, signature):
    if not GITHUB_SECRET:
        return True
    mac = hmac.new(GITHUB_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    expected_signature = 'sha256=' + mac.hexdigest()
    return hmac.compare_digest(expected_signature, signature)

# Webhook listener
@webhook.route("", methods=["POST"])  # Handles POST to /webhook
def receive_webhook():
    raw_data = request.data
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(raw_data, signature):
        logging.warning("❌ Signature verification failed.")
        abort(403, "Invalid signature")

    data = request.get_json(force=True)
    event = request.headers.get("X-GitHub-Event", "")

    logging.info(f"📦 Received webhook event: {event} with data: {data}")

    # Handle ping event (GitHub webhook test)
    if event == "ping":
        return jsonify({"msg": "pong"}), 200

    payload = {}

    if "pusher" in data:
        payload = {
            "request_id": data.get("after"),
            "author": data.get("pusher", {}).get("name"),
            "action": "PUSH",
            "from_branch": data.get("ref", "").split("/")[-1],
            "to_branch": data.get("ref", "").split("/")[-1],
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        }

    elif "pull_request" in data:
        action = "MERGE" if data.get("action") == "closed" and data["pull_request"].get("merged") else "PULL_REQUEST"
        payload = {
            "request_id": str(data["pull_request"].get("id")),
            "author": data.get("sender", {}).get("login"),
            "action": action,
            "from_branch": data["pull_request"]["head"].get("ref"),
            "to_branch": data["pull_request"]["base"].get("ref"),
            "timestamp": datetime.utcnow().strftime("%d %B %Y - %I:%M %p UTC")
        }

    if payload:
        collection.insert_one(payload)
        logging.info(f"✅ Event saved: {payload}")
        return jsonify({"status": "saved", "data": payload}), 200

    logging.warning("⚠️ Invalid data received.")
    return jsonify({"error": "invalid data"}), 400

# API to retrieve events
@webhook.route("/api/events", methods=["GET"])
def get_events():
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data), 200
