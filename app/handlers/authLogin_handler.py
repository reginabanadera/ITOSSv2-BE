from flask import Flask, jsonify, request, session, current_app, g
from database import db
from app.models.itoss.tblUsers import Users
from app.models.kweph_mfa.tblConsolidated import Users_MFA
from app.services.encryption_services import hash_password
from sqlalchemy import and_, text
from app.services.jwt_validator import token_required
from datetime import datetime, timedelta
import os
import jwt

def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    hash_pass = hash_password(password)

    try:
        itoss_user = Users.query.filter(Users.EmployeeId == username).first()
        if itoss_user:

            user = Users_MFA.query.filter(
                and_ (
                    Users_MFA.EmployeeId == username,  # ← This is from the wrong model
                    Users_MFA.Password == hash_pass
                )
            ).first()

            if user:
                token = jwt.encode({
                    'user_id': user.id,
                    'username': user.EmployeeName,   #  add username
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }, current_app.config['SECRET_KEY'], algorithm='HS256')

                response = jsonify({"message": "Login successful!", "status" : "success", "user":user.EmployeeId})
                response.set_cookie(
                    key="access_token",
                    value =token,
                    httponly=True,     # Can't be accessed by JS
                    secure=True,       # Only sent over HTTPS
                    samesite="None", # Prevents CSRF in most cases
                    max_age=3600       # Optional: auto-expire in 1 hour
                )

                return response, 200

            else:
                return jsonify({"message": "MFA : Invalid credentials!", "status": "error"}), 401
        else:
            return jsonify({"message": "ITOSS : User does not exist!", "status": "error"}), 404
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

@token_required
def validate_token():
    return jsonify({"message": "Token is valid!", "user": g.payload['username']}), 200
    
def test_db_connection():
    try:
        # Simple raw SQL query  
        result = db.session.execute(text("SELECT 1")).scalar()
        return jsonify({"db_connection": "success", "result": result})
    except Exception as e:
        return jsonify({"db_connection": "failed", "error": str(e)}), 500
    

@token_required
def validatePass():
    user = g.payload['user_id']
    data = request.json
    password = data.get('password')
    hash_pass = hash_password(password)

    confirm = Users_MFA.query.filter(
        and_(
            Users_MFA.id == user,
            Users_MFA.Password == hash_pass
        )
    ).first()
    if confirm:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Invalid password"}), 401