from database import db
from app.models.itoss.tblConfigTicketCategories import TicketCategory
from app.models.itoss.tblConfigTicketCustomFields import TicketCustomFields
from app.models.itoss.tblConfigTicketCategApprover import TicketApproverLevel
from flask import jsonify, request, g
from app.services.jwt_validator import token_required
from datetime import datetime
import pytz
# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)

# Format to YYYY-MM-DD
formatted_date = now_ph.strftime("%Y-%m-%d")

@token_required
def fetchAllTicketCateg():
    try:
        categs = TicketCategory.query.all()

        if not categs:
            return jsonify({"error": "No ticket categories found"}), 404  # Not Found is more appropriate

        return jsonify([categ.to_dict() for categ in categs]), 200

    except Exception as e:
        import traceback
        print("=== ERROR FETCHING CATEGORIES ===")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500
    

@token_required
def createTicketCateg():
    try:
        data = request.get_json()

        name = data.get("name")
        parent_id = data.get("ParentId")
        custom_fields = data.get("CustomFields", [])
        approvers = data.get("ApproverLevel", [])
        current_user = g.payload['username']

        #CreateCategory 
        category = TicketCategory(Name=name, ParentId=parent_id, CreatedBy=current_user)

        db.session.add(category)
        db.session.flush()  # get category.SystemId

        category_id = category.SystemId

        for field in custom_fields:
            new_field = TicketCustomFields(
                CategoryId = category_id,
                FieldName = field.get("FieldName"),
                FieldType = field.get("FieldType"),
                FieldLabel = field.get("FieldLabel"),
                SelectSourceType = field.get("SelectSourceType"),
                SelectSourceValue = field.get("ValueColumn"),
                CreatedBy=current_user
            )

            db.session.add(new_field)

        for approver in approvers:
            new_approver = TicketApproverLevel(
                CategoryId = category_id,
                LevelNo = approver.get("LevelNo"),
                ApproverType = approver.get("ApproverType"),
                ApproverValue = approver.get("ApproverValue"),
                CreatedBy = current_user
            )

            db.session.add(new_approver)

        db.session.commit()

        return jsonify({
            "message": "Ticket category created successfully!"
        }), 200
    
    except Exception as e:
        import traceback
        print("=== ERROR CREATING CATEGORIES ===")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500