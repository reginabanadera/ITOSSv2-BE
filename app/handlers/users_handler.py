from flask import Flask, jsonify, request
from database import db
from app.models.itoss.tblUsers import Users
from app.services.jwt_validator import token_required

@token_required
def fetchUser(id):
    user = Users.query.filter(Users.EmployeeId == id).first()
    return (jsonify(user.to_dict()))