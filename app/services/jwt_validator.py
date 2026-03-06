from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            g.payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403

        return f(*args, **kwargs)
    return decorated
