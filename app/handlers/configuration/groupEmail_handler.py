from database import db
from app.models.itoss.tblConfigGroupEmails import GroupEmails
from flask import jsonify, request, g
from app.services.jwt_validator import token_required
from datetime import datetime
import pytz
# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)


@token_required
def fetchAllGroupEmail():
    try:
        groups = GroupEmails.query.all()

        if not groups:
            return jsonify({"error": "No group email found"}), 404  # Not Found is more appropriate

        return jsonify([group.to_dict() for group in groups]), 200

    except Exception as e:
        return jsonify({"error": f"Error fetching group email: {str(e)}"}), 500
    

@token_required
def createNewGroup():
    data = request.json
    # Get username from the decoded token
    current_user = g.payload['username']
    status = "1"
    
    valid_fields = {col.name for col in GroupEmails.__table__.columns}
    filtered_data = {k: v for k, v in data.items() if k in valid_fields}

    existing = GroupEmails.query.filter(GroupEmails.GroupEmail == filtered_data.get("GroupEmail")).first()
    if existing:
        return jsonify({"error": "Group email already exists"}), 409

    group = GroupEmails(**filtered_data, Added_By=current_user, Status = status)
    db.session.add(group)
    db.session.commit()

    return jsonify({"message": "Group email created", "creator": current_user}), 200


@token_required
def editGroup():
    data = request.get_json()
    SystemId = data.get("SystemId")

    group = GroupEmails.query.get(SystemId)
    if not group:
        return jsonify({"message": "Group profile not found"}), 404

    updating_fields = [
        "GroupName", "GroupEmail", "Status" 
    ]

    for field in updating_fields:
        if field in data:
            setattr(group, field, data[field])

    group.ModifiedBy = g.payload['username']
    group.DateModified = datetime.now(ph_tz).strftime("%Y-%m-%d %H:%M:%S") 
    db.session.commit()

    return jsonify({"message": "Group profile updated successfully"}), 200