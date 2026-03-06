from flask import jsonify, request, g
from app.services.jwt_validator import token_required
from app.models.itoss.tblInvAssetRequisition import AssetRequisition
from database import db
import pandas as pd
import pytz
from datetime import datetime
from sqlalchemy import or_
import requests


# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)



@token_required
def uploadInvData():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        ext = file.filename.rsplit('.', 1)[1].lower()
        allowed_extensions = ['xlsx', 'xls', 'csv']
        if ext not in allowed_extensions:
            return jsonify({"error": "Invalid file type"}), 400

        # Read the Excel using pandas
        df = pd.read_excel(file) if ext != "csv" else pd.read_csv(file)

        # Required Columns
        required = ["Serial Number", "Model", "Brand", "Type", "Company", "Classification", "Cost", "Date Acquired"]
        missing = [col for col in required if col not in df.columns]

        if missing:
            return jsonify({
                "error": "Missing required columns",
                "missing_columns": missing
            }), 400


        df["Serial Number"] = df["Serial Number"].astype(str).str.strip()

        uploaded_serials = df["Serial Number"].unique().tolist()

        existing_serials = {
            s[0] for s in db.session.query(AssetRequisition.SerialNumber)
            .filter(AssetRequisition.SerialNumber.in_(uploaded_serials))
            .all()
        }

        # Convert rows to model objects
        assets, skipped = [], []

        for _, row in df.iterrows():
            serial = row["Serial Number"]

            if serial in existing_serials:
                skipped.append(serial)
                continue

            assets.append(AssetRequisition(
                SerialNumber=serial,
                Model=row["Model"],
                Brand=row["Brand"],
                EType=row["Type"],
                Company=row["Company"],
                Classification=row["Classification"],
                Cost=row["Cost"],
                DateAcquired=pd.to_datetime(row["Date Acquired"], errors="coerce")
            ))

        db.session.bulk_save_objects(assets)
        db.session.commit()

        return jsonify({
            "inserted": len(assets),
            "duplicates_skipped": len(skipped),
            "duplicate_serials": skipped
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()  # see full error in logs
        return jsonify({"error": str(e)}), 500

@token_required
def fetchAllAssetRequsition():
    assets = AssetRequisition.query.order_by(AssetRequisition.SerialNumber.asc()).all()
    return jsonify([asset.to_dict() for asset in assets])

@token_required
def check_serial():
    data = request.get_json()
    serial = data.get("serial_number")


    if not serial:
        return jsonify({
            "message" : "Serial Number is required!"
        }), 400
    
    item = AssetRequisition.query.filter_by(SerialNumber = serial).first()

    if not item:
        return({
            "serial": serial,
            "exists": False,
            "message": "Serial not found!"
        }), 200
    
    item.Existing = 1
    db.session.commit()

    return jsonify({
        "serial": serial,
        "exists": True,
        "message": "Serial exists, status updated!"
    }), 200


@token_required
def updateAsset_details(id):
    try:
        data = request.get_json()
        current_user = g.payload['username']

        asset = AssetRequisition.query.get(id)
        if not asset:
            return jsonify({"message": "Record not found!"}), 404
        
        updating_fields = [
            "ItemDescription", "AccountName", "Model", "Brand", "EType" 
        ]

        for field in updating_fields:
            if field in data:
                setattr(asset, field, data[field])

        asset.Date_Modified = datetime.now(ph_tz).strftime("%Y-%m-%d %H:%M:%S") 
        asset.ModifiedBy= current_user
        db.session.commit()

        return jsonify({"message": "Record successfully updated!" }), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            "message": "Error updating record",
            "error": f"{type(e).__name__}: {str(e)}"
        }), 500

@token_required
def reqAssetTag():
    PISYS_URL = "http://172.16.65.22/_api/_get_itoss_reqas.php"

    current_user = g.payload['user']
    sent_count = 0
    
    try:
        items = AssetRequisition.query.filter(
            AssetRequisition.Tagged == 0,
            or_(
                AssetRequisition.Existing.is_(None),
                AssetRequisition.Existing == 0
            ).all()
        )

        for item in items:
            try:
                print(f"{item.SerialNumber} / {item.EType}")

                payload = {
                    "serial_number": item.SerialNumber,
                    "model": item.Model,
                    "brand": item.Brand,
                    "unit_type": item.EType,
                    "cost": item.Cost,
                    "date_acquired": item.DateAcquired,
                    "account_name": item.AccountName,
                    "classification": item.Classification,
                    "company": item.Company,
                    "particulars": item.EType,
                    "item_description": item.ItemDescription,
                    "empid": current_user
                }

                 # POST REQUEST (replaces CURL)
                response = requests.post(
                    PISYS_URL,
                    data=payload,
                    timeout=10
                )

                if response.ok:
                    sent_count += 1

            except Exception as row_err:
                print(f"Row error ({item.SerialNumber}): {row_err}")

        return jsonify({
            "status": "success",
            "sent": sent_count,
            "total": len(items)
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



