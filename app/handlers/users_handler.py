from flask import Flask, jsonify, request
from database import db
from app.models.itoss.tblUsers import Users
from app.models.hris.vwAtKWE import vwAtKWE
from app.services.jwt_validator import token_required

@token_required
def fetchUser(id):
    user = vwAtKWE.query.filter(vwAtKWE.EmployeeId == id).first()

    user_group = Users.query.filter(
        Users.EmployeeId == id
    ).first()

    data = user.to_dict()
    data["UserGroup"] = user_group.UserGroup if user_group else None

    return jsonify(data)
    #return (jsonify(user.to_dict()))


def testing():
    return "API is working!"