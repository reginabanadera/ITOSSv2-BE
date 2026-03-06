from database import db
from app.models.itoss.vwEmailAddress import vwEmailAddress
from app.models.itoss.tblConfigEmailAddress import EmailAddress
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


@token_required
def fetchAllEmailAddress():
    emails = vwEmailAddress.query.order_by(vwEmailAddress.FullName.asc()).all()
    return jsonify([email.to_dict() for email in emails])

@token_required
def UpdateEmailDetail(id):
    try:
        data = request.get_json()

        column = EmailAddress.query.get(id)
        if not column:
            return jsonify({"message": "Email Address not found"}), 404

        updating_fields = [
            "EmailAddress", "Date_Created", "Date_Deleted", "Status"
        ]

        for field in updating_fields:
            if field in data:
                setattr(column, field, data[field])

        column.ModifiedBy = g.payload['username']
        column.DateModified = datetime.now(ph_tz).strftime("%Y-%m-%d %H:%M:%S") 
        db.session.commit()

        return jsonify({"message": "Email details has been successfully updated!"}), 200
    
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()  # see full error in logs
        return jsonify({
            "message": "Error updating email profile",
            "error": f"{type(e).__name__}: {str(e)}"
        }), 500
