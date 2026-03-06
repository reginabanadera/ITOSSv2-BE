from database import db
from app.models.itoss.tblConfigTicketCategories import TicketCategory
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