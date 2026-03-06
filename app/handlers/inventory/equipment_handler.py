from flask import jsonify, request, g
from app.services.jwt_validator import token_required
from app.models.itoss.tblInvEquipment import EquipmentInv
from app.models.hris.vwAtKWE import vwAtKWE
from app.models.itoss.tblInvAssetRequisition import AssetRequisition
from app.models.itoss.tblInvEquipment_History import InvEquipment_History
from database import db
from sqlalchemy import case, func, and_
from datetime import datetime
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

@token_required
def getEquipment():
    try:
        equips = (
            db.session.query(
                EquipmentInv,
                vwAtKWE,
                AssetRequisition
            )
            .outerjoin(
                AssetRequisition,
                EquipmentInv.AssetTag == AssetRequisition.AssetTag
            )
            .outerjoin(
                vwAtKWE,
                EquipmentInv.EmployeeId.collate("SQL_Latin1_General_CP1_CI_AS")
                == vwAtKWE.EmployeeId.collate("SQL_Latin1_General_CP1_CI_AS")
            )
            .all()
        )

        output = []
        for eq, vw, sn in equips:
            output.append({
                **eq.to_dict(),

                # vwAtKWE fields (same as before)
                "EmployeeName": vw.FullName if vw else None,
                "Section": vw.Section if vw else None,
                "Area": vw.Area if vw else None,
                "Department": vw.Department if vw else None,
                "Designation": vw.Designation if vw else None,

                # Computed fields (from your SELECT)
                "AssetModel": f"{eq.Brand}/ {eq.AssetTag}/ {eq.SerialNumber}"
                if eq.Brand and eq.AssetTag and eq.SerialNumber else None,

                "Status": (
                    "Disposed"
                    if eq.Remarks and "disposed" in eq.Remarks.lower()
                    else (
                        "Available" if sn and sn.Assigned == 0
                        else "Assigned" if sn and sn.Assigned == 1
                        else "No Records"
                    )
                ),

                # Serial table fields
                "Cost": sn.Cost if sn else None,
                "Company": sn.Company if sn else None,
            })

        return jsonify(output), 200

    except Exception as e:
        print(f"Error in fetchEquipment: {str(e)}")
        return jsonify({"error": f"Error fetching equipment: {str(e)}"}), 500
    
@token_required
def createEquip():
    data = request.json
    # Get username from the decoded token
    current_user = g.payload['username']
    temp = data.get("Temporary")
    
    valid_fields = {col.name for col in EquipmentInv.__table__.columns}
    filtered_data = {k: v for k, v in data.items() if k in valid_fields}

    existing = EquipmentInv.query.filter(
        and_(
            EquipmentInv.EmployeeId == filtered_data.get("EmployeeId"),
            EquipmentInv.SerialNumber == filtered_data.get("SerialNumber"),
            )
        ).first()
    
    if existing:
        return jsonify({"error": "Assignment already exists!"}), 409

    equip = EquipmentInv(**filtered_data, Added_By=current_user)
    db.session.add(equip)
    
    asset = AssetRequisition.query.filter(AssetRequisition.SerialNumber == filtered_data.get("SerialNumber")).first()
    if asset:
        asset.Existing = 1
        asset.Tagged = 1
        asset.Assigned = temp
        asset.ModifiedBy = current_user
        asset.DateModified = datetime.now(philippines_tz)
    else:
        description = f"{filtered_data.get("EqType")}-{filtered_data.get("Brand")}-{filtered_data.get("Model")}"
        company = "KWEPH"
        classification = "IT RELATED"
        accountname = (
            "Asset"
            if len(filtered_data.get("AssetTag").split("-")) > 1 and filtered_data.get("AssetTag").split("-")[1] == "1"
            else "Cost"
        )

        raw_cost = filtered_data.get("AccquiredCost")

        if raw_cost is None or not str(raw_cost).strip():
            cost = 0
        else:
            cost = float(raw_cost)

        new_asset = AssetRequisition(
            SerialNumber=filtered_data.get("SerialNumber"),
            AssetTag=filtered_data.get("AssetTag"),
            Model=filtered_data.get("Model"),
            Brand=filtered_data.get("Brand"),
            EType=filtered_data.get("EqType"),
            Company=company,
            ItemDescription = description,
            Classification = classification,
            AccountName= accountname,
            Cost=cost,
            DateAcquired = filtered_data.get("Year_Acquired"),
            EndofWarranty = filtered_data.get("EndofWarranty"),
            Existing=1,
            Tagged=1,
            Assigned=temp,
            AddedBy=current_user,
            DateCreated=datetime.now(philippines_tz)
        )
        db.session.add(new_asset)
        db.session.commit()

    return jsonify({"message": "The equipment has been successfully assigned!", "creator": current_user}), 200


@token_required
def releaseEquipment(serial):
    try:
        current_user = g.payload['username']
        equipment = EquipmentInv.query.filter_by(SerialNumber=serial).first()

        if not equipment:
            return jsonify({ "message": "Equipment not found" }), 404
        
        etype = equipment.EqType
        model = equipment.Model
        brand = equipment.Brand
        assetTag = equipment.AssetTag
        default_owner = "K1308"
        default_acccountedto = "K845"
        now = datetime.now(philippines_tz).replace(tzinfo=None)

        equipment.EmployeeId = default_owner
        equipment.AccountedTo = default_acccountedto
        equipment.Year_Issue = now
        equipment.Date_Modified = now
        equipment.Modified_By = current_user

        asset = AssetRequisition.query.filter_by(SerialNumber=serial).first()
        if asset:
            asset.Assigned = 0
            asset.ModifiedBy = current_user
            asset.DateModified = now

        history = InvEquipment_History.query.filter(
            and_(
                InvEquipment_History.SerialNumber == serial,
                InvEquipment_History.EmployeeId == default_owner
            )
        ).first()

        if not history:
            ins_history = InvEquipment_History(
                SerialNumber=serial,
                EmployeeId=default_owner,
                EType = etype,
                AssetTag=assetTag,
                Model=model,
                Brand=brand,
                AccountedTo=default_acccountedto,
                Added_By=current_user
            )

            db.session.add(ins_history)
        db.session.commit()

        return jsonify({ "message": f"{serial} released successfully" })

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 👈 print full stacktrace in console
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@token_required
def AssignEquipment():
    try:
        data = request.json
        # Get username from the decoded token
        current_user = g.payload['username']
        employee_id = data.get("EmployeeId")
        accounted_to = data.get("DeptHeadId")
        dateAssigned = data.get("dateAssigned")
        items = data.get("items", [])
        now = datetime.now(philippines_tz).replace(tzinfo=None)

        if not employee_id or not items:
            return jsonify({"message": "Invalid payload"}), 400

        for item in items:
            serial = item.get("serial")
            eqType = item.get("eqType")
            assetTag = item.get("assetTag")
            brand = item.get("brand")
            model = item.get("model")

            equipment = EquipmentInv.query.filter_by(SerialNumber=serial).first()
            if not equipment:
                raise Exception(f"Equipment not found: {serial}")

            # Update equipment
            equipment.EmployeeId = employee_id
            equipment.AccountedTo = accounted_to
            equipment.Year_Issued = dateAssigned
            equipment.Date_Modified = now
            equipment.Modified_By = current_user

            # Update asset requisition
            asset = AssetRequisition.query.filter_by(SerialNumber=serial).first()
            if asset:
                asset.Assigned = 1
                asset.ModifiedBy = current_user
                asset.DateModified = now

            # Insert history
            history = InvEquipment_History(
                SerialNumber=serial,
                AssetTag=assetTag,
                Model=model,
                Brand=brand,
                EType=eqType,
                EmployeeId=employee_id,
                AccountedTo=accounted_to,
                Added_By=current_user
            )
            db.session.add(history)

        db.session.commit()
        return jsonify({"message": "Equipment assigned successfully"}), 200

    except Exception as e:
        import traceback
        print(traceback.format_exc())  # 👈 print full stacktrace in console
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

        
