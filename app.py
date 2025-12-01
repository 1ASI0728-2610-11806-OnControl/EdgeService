"""Flask application entry point for the Smart Band Edge Service."""

from flask import Flask
from flasgger import Swagger
from flask_cors import CORS

import iam.application.services
from health.interfaces.services import health_api
from iam.interfaces.services import iam_api
from shared.infrastructure.database import init_db

app = Flask(__name__)
swagger = Swagger(app)
CORS(app, origins="*", allow_headers=["Authorization", "Content-Type", "X-API-Key", "ngrok-skip-browser-warning"], supports_credentials=True)


app.register_blueprint(iam_api)
app.register_blueprint(health_api)

first_request = True

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
    app.run(host="0.0.0.0", port=5000, debug=True)
