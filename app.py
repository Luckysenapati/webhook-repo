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
