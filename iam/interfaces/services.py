"""Interface services for the IAM bounded context."""
from flask import Blueprint, request, jsonify, g
from flasgger import swag_from
from iam.application.services import AuthApplicationService, DeviceOwnershipApplicationService
from shared.auth import require_jwt

iam_api = Blueprint("iam_api", __name__)

# Initialize dependencies
auth_service = AuthApplicationService()
device_ownership_service = DeviceOwnershipApplicationService()


def authenticate_request():
    """
    Authenticates a device's POST request.
    Ensures the request is JSON and contains the necessary device credentials.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    device_id = request.json.get("device_id")
    api_key = request.headers.get("X-API-Key")

    if not device_id or not api_key:
        return jsonify({"error": "Missing device_id in body or X-API-Key in header"}), 401
    
    if not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401
        
    return None


@iam_api.route("/devices/claim", methods=["POST"])
@require_jwt
@swag_from({
    'tags': ['Device Management'],
    'summary': 'Claim a device for the logged-in patient',
    'description': 'Allows a PATIENT to claim ownership of a specific device by its device_id.',
    'parameters': [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "User JWT. Format: Bearer <token>"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "required": ["device_id"],
                "properties": {
                    "device_id": {"type": "string", "description": "The unique ID of the device to claim."}
                }
            }
        }
    ],
    'consumes': ['application/json'],
    'responses': {
        '200': {'description': 'Device claimed successfully.'},
        '400': {'description': 'Bad Request (e.g., missing device_id).'},
        '401': {'description': 'Unauthorized (invalid, expired, or missing token).'},
        '403': {'description': 'Forbidden (only PATIENT role can claim devices, or device already claimed by another).'},
        '415': {'description': 'Content-Type must be application/json.'}
    }
})
def claim_device_endpoint():
    """Endpoint for patients to claim ownership of a device."""
    user_info = g.user
    
    if user_info['profileType'] != 'PATIENT':
        return jsonify({"error": "Only PATIENT users can claim devices"}), 403

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.json
    device_id = data.get("device_id")

    if not device_id:
        return jsonify({"error": "Missing device_id in request body"}), 400

    try:
        device_ownership_service.claim_device(user_info['profileId'], device_id)
        return jsonify({"message": f"Device {device_id} claimed successfully by patient {user_info['profileId']}"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403 # Using 403 as it's a permission/ownership issue
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
