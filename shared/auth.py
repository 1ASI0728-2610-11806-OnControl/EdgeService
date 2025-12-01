from functools import wraps
from flask import request, jsonify, g
import jwt

# The secret key provided by the user (From Central Backend Envs).
JWT_SECRET_KEY = "0dfdddd9-20e4-4aa4-9967-4782dad8cdb3"

def require_jwt(f):
    """
    A decorator to protect endpoints with JWT authentication.
    It verifies the token signed by the Central Backend using the shared secret.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401
            
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
             return jsonify({"error": "Authorization header must be in the format 'Bearer <token>'"}), 401
             
        token = parts[1]
        
        try:
            # Decode the token using the shared secret from the Central Backend
            # We verify the signature to ensure the token was issued by the trusted Backend
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            
            # DEBUG: Print payload to console to verify structure (profileType vs role, etc.)
            print(f"DEBUG: Decoded JWT Payload: {payload}")
            
            # Store payload in global context for the endpoint to use
            g.user = payload
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            print(f"DEBUG: Token Validation Error: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
            
        return f(*args, **kwargs)
    return decorated_function
