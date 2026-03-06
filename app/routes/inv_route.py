from flask import Blueprint
from app.handlers.inventory.assetRequisition_handler import uploadInvData, fetchAllAssetRequsition, check_serial, updateAsset_details, reqAssetTag
from app.handlers.inventory.equipment_handler import getEquipment, createEquip, releaseEquipment, AssignEquipment

inv_bp = Blueprint("inv", __name__) 

#ASSET REQUISITION
inv_bp.route("/upload-assetReq-excel", methods=["POST"])(uploadInvData)
inv_bp.route("/getAssetReq", methods=["GET"])(fetchAllAssetRequsition)
inv_bp.route("/check-serial", methods=["POST"])(check_serial)
inv_bp.route("/updAsset/<id>", methods=["PUT"])(updateAsset_details)
inv_bp.route("/reqAssetTag", methods=["POST"])(reqAssetTag)

#EQUIPMENT
inv_bp.route("/getEquipment", methods=["GET"])(getEquipment)
inv_bp.route("/AddEquip", methods=["POST"])(createEquip)
inv_bp.route("/relEquip/<serial>", methods=["PUT"])(releaseEquipment) 
inv_bp.route("/AssignUnit", methods=["POST"])(AssignEquipment)






