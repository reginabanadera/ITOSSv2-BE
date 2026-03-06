from flask import Blueprint
from app.handlers.authLogin_handler import login, test_db_connection, validate_token, validatePass

auth_bp = Blueprint("auth", __name__)

auth_bp.route("/login", methods=["POST"])(login)
auth_bp.route("/verify_token", methods=["GET"])(validate_token)
auth_bp.route("/confirmPass", methods=["POST"])(validatePass)
auth_bp.route("/testdb", methods=["GET"])(test_db_connection)