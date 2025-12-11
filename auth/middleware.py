from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            # Cria um objeto mock para simular o current_user
            class CurrentUser:
                id = claims.get("sub")
                role = claims.get("role")
                tenant_id = claims.get("tenant_id")
            
            return f(CurrentUser(), *args, **kwargs)
        except Exception as e:
            return jsonify({"message": "Token invalido ou ausente", "error": str(e)}), 401
    return decorated

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != role:
                return jsonify({"message": "Acesso negado"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
