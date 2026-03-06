from database import db
from app.models.hris.vwAtKWE import vwAtKWE
from flask import jsonify, request, g
from app.services.jwt_validator import token_required
from datetime import datetime
from sqlalchemy import text
import pytz
import os


# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)


# @token_required
def fetchAllEmployees():
    employees = vwAtKWE.query.filter_by(Tag ='Active').order_by(vwAtKWE.FullName.asc()).all()
    return jsonify([employee.to_dict() for employee in employees])