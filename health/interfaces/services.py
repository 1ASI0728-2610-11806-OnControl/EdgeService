import json
import logging
import os
import urllib.error
import urllib.request

from flask import Blueprint, request, jsonify, g
from flasgger import swag_from
from health.application.services import HealthRecordApplicationService
from iam.interfaces.services import authenticate_request
from shared.auth import require_jwt
from iam.application.services import DeviceOwnershipApplicationService # New import

health_api = Blueprint("health_api", __name__)
logger = logging.getLogger(__name__)

# Initialize dependencies
health_record_service = HealthRecordApplicationService()
device_ownership_service = DeviceOwnershipApplicationService() # New initialization

DEFAULT_AI_EXPLANATION = (
    "Se detectaron valores fuera del rango esperado en oxigenación, temperatura y ritmo cardíaco. "
    "Revise el panel del paciente para priorizar el seguimiento."
)

# --- Reusable Swagger/OpenAPI Schema Definitions ---
health_record_def = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "device_id": {"type": "string"},
        "bpm": {"type": "number"},
        "temp": {"type": "number"},
        "temperature": {"type": "number"},
        "spo2": {"type": "number"},
        "created_at": {"type": "string", "format": "date-time"},
        "riskScore": {"type": "number"},
        "riskLevel": {"type": "string"},
        "reasons": {"type": "array", "items": {"type": "string"}},
        "aiExplanation": {"type": "string"}
    }
}

health_record_input_def = {
    "type": "object",
    "required": ["device_id", "bpm", "temp", "spo2"],
    "properties": {
        "device_id": {"type": "string"},
        "bpm": {"type": "number"},
        "temp": {"type": "number"},
        "spo2": {"type": "number"},
        "created_at": {"type": "string", "format": "date-time", "description": "Optional."}
    }
}


def format_created_at(created_at):
    """Return a compact ISO timestamp suitable for JSON responses."""
    return created_at.isoformat().replace("+00:00", "Z")


def calculate_predictive_risk(bpm: float, temp: float, spo2: float) -> dict:
    """Calculate a local predictive risk score from vital signs.

    This function does not call an LLM. It only produces a deterministic score,
    level and reason list so the external local AI can redact a short message.
    """
    bpm = float(bpm)
    temp = float(temp)
    spo2 = float(spo2)

    score = 0
    reasons: list[str] = []

    if spo2 < 95:
        score += 30
        reasons.append("SpO2 baja")
    if spo2 < 92:
        score += 20

    if bpm > 110:
        score += 20
        reasons.append("BPM alto")
    elif bpm < 50:
        score += 20
        reasons.append("BPM bajo")

    if temp > 37.8:
        score += 20
        reasons.append("temperatura elevada")
    if temp > 38.5:
        score += 10
    elif temp < 35.5:
        score += 15
        reasons.append("temperatura baja")

    score = min(score, 100)

    if score <= 39:
        level = "LOW"
    elif score <= 69:
        level = "MODERATE"
    else:
        level = "HIGH"

    if not reasons:
        reasons.append("valores dentro del rango esperado")

    return {
        "riskScore": score,
        "riskLevel": level,
        "reasons": reasons
    }


def is_local_ai_enabled() -> bool:
    """Return whether the optional local AI integration is enabled."""
    return os.getenv("LOCAL_AI_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")


def call_local_ai_explanation(bpm: float, temp: float, spo2: float, risk: dict) -> str:
    """Call the local AI proxy exposed with Cloudflare Tunnel.

    Falls back to a safe default explanation when the proxy is disabled, unavailable,
    slow or returns an unexpected response.
    """
    if not is_local_ai_enabled():
        logger.info("Local AI disabled. Using fallback explanation.")
        return DEFAULT_AI_EXPLANATION

    base_url = os.getenv("LOCAL_AI_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv("LOCAL_AI_API_KEY", "").strip()
    timeout_ms_raw = os.getenv("LOCAL_AI_TIMEOUT_MS", "6000").strip()

    if not base_url or not api_key:
        logger.warning("Local AI env vars missing. Using fallback explanation.")
        return DEFAULT_AI_EXPLANATION

    try:
        timeout_seconds = max(float(timeout_ms_raw) / 1000, 0.5)
    except ValueError:
        timeout_seconds = 6.0

    payload = {
        "bpm": float(bpm),
        "spo2": float(spo2),
        "temperature": float(temp),
        "riskScore": risk["riskScore"],
        "riskLevel": risk["riskLevel"],
        "reasons": risk["reasons"]
    }

    try:
        request_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/risk-explanation",
            data=request_data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Local-AI-Key": api_key
            }
        )

        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body)

        explanation = str(parsed.get("explanation", "")).strip()
        if explanation:
            logger.info("Local AI explanation generated successfully.")
            return explanation

        logger.warning("Local AI returned an empty explanation. Using fallback.")
        return DEFAULT_AI_EXPLANATION

    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("Local AI call failed. Using fallback explanation. Error: %s", exc)
        return DEFAULT_AI_EXPLANATION


def serialize_health_record(record, include_id=True, include_ai=False):
    """Serialize a health record with the risk status expected by clients."""
    is_critical = health_record_service.check_health_risk(record.bpm, record.temp, record.spo2)
    risk = calculate_predictive_risk(record.bpm, record.temp, record.spo2)

    payload = {
        "device_id": record.device_id,
        "bpm": record.bpm,
        "temp": record.temp,
        "temperature": record.temp,
        "spo2": record.spo2,
        "created_at": format_created_at(record.created_at),
        "is_critical": is_critical,
        "riskScore": risk["riskScore"],
        "riskLevel": risk["riskLevel"],
        "reasons": risk["reasons"]
    }

    if include_ai:
        payload["aiExplanation"] = call_local_ai_explanation(record.bpm, record.temp, record.spo2, risk)

    if include_id:
        payload["id"] = record.id
    return payload


# --- GET Endpoint for Logged-in Users (JWT Auth) ---
@health_api.route("/OnControl/parameters", methods=["GET"])
@require_jwt
@swag_from({
    'tags': ['Health Monitoring (Users)'],
    'summary': 'Retrieve health data records based on user role',
    'description': 'For DOCTORs, returns all records. For PATIENTs, returns only their own records based on their profileId.',
    'parameters': [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "User JWT. Format: Bearer <token>"
        }
    ],
    'responses': {
        '200': {
            'description': 'A list of health records.',
            'schema': {'type': 'array', 'items': health_record_def}
        },
        '401': {'description': 'Unauthorized (invalid, expired, or missing token).'},
        '403': {'description': 'Forbidden (user role cannot access this data).'}
    }
})
def get_health_records():
    """Fetches health records based on the JWT user's role."""
    user_info = g.user

    if user_info['profileType'] == 'DOCTOR':
        records = health_record_service.get_all_health_records()
    elif user_info['profileType'] == 'PATIENT':
        patient_profile_id = user_info['profileId']
        owned_device_ids = device_ownership_service.get_devices_for_patient(patient_profile_id)

        if not owned_device_ids:
            records = [] # No devices claimed by this patient
        else:
            records = health_record_service.get_records_for_devices(owned_device_ids)
    else:
        return jsonify({"error": "Your user profile type cannot access this data"}), 403

    result = [serialize_health_record(record) for record in records]
    return jsonify(result), 200


# --- GET Latest Endpoint for Patients (JWT Auth) ---
@health_api.route("/OnControl/parameters/latest", methods=["GET"])
@require_jwt
@swag_from({
    'tags': ['Health Monitoring (Users)'],
    'summary': 'Retrieve the latest health data record for a patient',
    'description': 'Fetches only the single most recent health data record for the logged-in PATIENT.',
    'parameters': [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "User JWT. Format: Bearer <token>"
        }
    ],
    'responses': {
        '200': {
            'description': 'The latest health record.',
            'schema': health_record_def
        },
        '401': {'description': 'Unauthorized (invalid, expired, or missing token).'},
        '403': {'description': 'Forbidden (only PATIENT role can access this).'},
        '404': {'description': 'Not Found (no records found for this patient).'}
    }
})
def get_latest_health_record():
    """Fetches the latest health record for the logged-in patient."""
    user_info = g.user

    if user_info['profileType'] != 'PATIENT':
        return jsonify({"error": "This endpoint is only for users with the PATIENT profile type"}), 403

    patient_profile_id = user_info['profileId']
    owned_device_ids = device_ownership_service.get_devices_for_patient(patient_profile_id)

    if not owned_device_ids:
        return jsonify({"error": "No devices claimed by this patient"}), 404

    record = health_record_service.get_latest_record_for_devices(owned_device_ids)

    if not record:
        return jsonify({"error": "No health records found for claimed devices"}), 404

    result = serialize_health_record(record)
    return jsonify(result), 200


# --- GET Latest Endpoint for Academic Demo (No JWT) ---
@health_api.route("/OnControl/parameters/latest-demo", methods=["GET"])
@swag_from({
    'tags': ['Health Monitoring (Demo)'],
    'summary': 'Retrieve the latest demo health data record without JWT',
    'description': 'Fetches the most recent record for the configured demo device.',
    'responses': {
        '200': {
            'description': 'The latest demo health record.',
            'schema': health_record_def
        },
        '404': {'description': 'Not Found (no demo records found).'}
    }
})
def get_latest_health_record_demo():
    """Fetch the latest record for the configured demo device without JWT."""
    demo_device_id = os.getenv("DEVICE_ID", "smart-band-001")
    record = health_record_service.get_latest_record_for_device(demo_device_id)

    if not record:
        return jsonify({"error": "No health records found for demo device"}), 404

    return jsonify(serialize_health_record(record, include_id=False, include_ai=True)), 200


# --- POST Endpoint for Devices (API Key Auth) ---
@health_api.route("/OnControl/parameters", methods=["POST"])
@swag_from({
    'tags': ['Health Monitoring (Devices)'],
    'summary': 'Submit a new health data record from a device',
    'parameters': [
        {
            "name": "X-API-Key",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "The API key for the device."
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": health_record_input_def
        }
    ],
    'consumes': ['application/json'],
    'responses': {
        '201': {
            'description': 'Record created successfully.',
            'schema': health_record_def
        },
        '400': {'description': 'Bad Request (e.g., missing fields).'},
        '401': {'description': 'Authentication failed (invalid API key or device_id).'},
        '415': {'description': 'Content-Type must be application/json.'}
    }
})
def create_health_record():
    """Creates a new health record from device data."""
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        device_id = data["device_id"]
        bpm = data["bpm"]
        temp = data["temp"]
        spo2 = data["spo2"]
        created_at = data.get("created_at")

        # Service now returns a tuple: (record, trigger_alert)
        record, trigger_alert = health_record_service.create_health_record(
            device_id, bpm, temp, spo2, created_at, request.headers.get("X-API-Key")
        )

        risk = calculate_predictive_risk(record.bpm, record.temp, record.spo2)
        response_payload = {
            "id": record.id,
            "device_id": record.device_id,
            "bpm": record.bpm,
            "temp": record.temp,
            "temperature": record.temp,
            "spo2": record.spo2,
            "created_at": format_created_at(record.created_at),
            "is_critical": trigger_alert,
            "riskScore": risk["riskScore"],
            "riskLevel": risk["riskLevel"],
            "reasons": risk["reasons"],
            "actuator_command": {
                "alarm": trigger_alert
            }
        }
        return jsonify(response_payload), 201
    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
