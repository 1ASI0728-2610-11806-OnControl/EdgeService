"""Flask application entry point for the Smart Band Edge Service."""

import os

from flask import Flask, jsonify
from flasgger import Swagger
from flask_cors import CORS

import iam.application.services
from health.interfaces.services import health_api
from iam.interfaces.services import iam_api
from shared.infrastructure.database import init_db

def get_cors_origins() -> list[str]:
    """Read allowed CORS origins from a comma-separated environment variable."""
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return origins or ["http://localhost:3000"]


app = Flask(__name__)
swagger = Swagger(app)
CORS(
    app,
    origins=get_cors_origins(),
    allow_headers=["Authorization", "Content-Type", "X-API-Key", "ngrok-skip-browser-warning"],
    supports_credentials=True,
)

app.register_blueprint(iam_api)
app.register_blueprint(health_api)

first_request = True


@app.route("/status", methods=["GET"])
def status():
    """Service health check for local and deploy smoke tests."""
    return jsonify({
        "status": "ok",
        "service": "EdgeService",
        "message": "Service running"
    }), 200


@app.before_request
def setup():
    """Initialize the database and create a test device before the first request."""
    global first_request
    if first_request:
        first_request = False
        init_db()
        auth_application_service = iam.application.services.AuthApplicationService()
        auth_application_service.get_or_create_test_device()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "production").lower() == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
