from functools import wraps
from flask import request, jsonify, current_app, g
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # ✅ ONLY COOKIE (no headers)
        token = request.cookies.get("access_token")

        #print("COOKIE TOKEN:", token)  # DEBUG

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            g.payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"],
                audience="itoss-client",
                issuer="ITOSSv2"
            )

        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401

        except jwt.InvalidAudienceError:
            return jsonify({"message": "Invalid audience!"}), 403

        except jwt.InvalidIssuerError:
            return jsonify({"message": "Invalid issuer!"}), 403

        except jwt.InvalidTokenError as e:
            print("JWT ERROR:", repr(e))
            return jsonify({"message": "Invalid token!"}), 403

        except Exception as e:
            print("UNEXPECTED ERROR:", repr(e))
            return jsonify({"message": "Token validation failed"}), 403

        return f(*args, **kwargs)

    return decorated