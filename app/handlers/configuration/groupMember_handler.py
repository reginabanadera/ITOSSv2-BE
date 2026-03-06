from database import db
from app.models.itoss.tblConfigGroupMembers import GroupMembers
from app.models.hris.vwAtKWE import vwAtKWE
from flask import jsonify, request, g
from app.services.jwt_validator import token_required
from datetime import datetime
from sqlalchemy import literal_column
import pytz
# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)


@token_required
def fetchAllGroupMembers(ge):
    try:
        #members = GroupMembers.query.filter_by(GroupMembers.GroupEmail == ge ).order_by(GroupMembers.GroupEmail.asc()).all()

        members = (
            db.session.query(GroupMembers, vwAtKWE)
            .join(
                vwAtKWE,
                GroupMembers.EmployeeId.collate("SQL_Latin1_General_CP1_CI_AS")
                == vwAtKWE.EmployeeId.collate("SQL_Latin1_General_CP1_CI_AS")
            )
            .filter(GroupMembers.GroupEmail == ge)
            .all()
        )

        if not members:
            return jsonify([]), 200  # Not Found is more appropriate
        
        output = []
        for gm, vw in members:
            output.append({
                **gm.to_dict(),
                "FullName": vw.FullName,
                "Department": vw.Department
            })


        return jsonify(output), 200

    except Exception as e:
        print(f"Error in fetchAllGroupMembers: {str(e)}")
        return jsonify({"error": f"Error fetching group member: {str(e)}"}), 500
    

@token_required
def addGroupMember():
    data = request.json
    # Get username from the decoded token
    current_user = g.payload['username']
    
    valid_fields = {col.name for col in GroupMembers.__table__.columns}
    filtered_data = {k: v for k, v in data.items() if k in valid_fields}

    existing = GroupMembers.query.filter(
        GroupMembers.GroupEmail == filtered_data.get("GroupEmail"),
        GroupMembers.EmailAddress == filtered_data.get("EmailAddress")
    ).first()

    if existing:
        return jsonify({"warning": "Group member already exists!"}), 409

    member = GroupMembers(**filtered_data, Added_By=current_user)
    db.session.add(member)
    db.session.commit()

    return jsonify({"message": "Group member successfully added!", "creator": current_user}), 200


@token_required
def deleteMember(id):
    current_user = g.payload['username']

    existing = GroupMembers.query.filter(GroupMembers.SystemId == id).first()

    if not existing:
        return jsonify({"error": "Group member not found"}), 404

    # Delete the member
    db.session.delete(existing)
    db.session.commit()

    return jsonify({
        "message": "Group member successfully deleted!",
        "deleted_by": current_user
    }), 200

