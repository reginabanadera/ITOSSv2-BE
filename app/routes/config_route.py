from flask import Blueprint
from app.handlers.users_handler import fetchUser, testing
from app.handlers.configuration.systemProfile_handler import fetchAllSystems, createNewProfile, updateProfile
from app.handlers.configuration.dbColumns_handler import fetchAllDBColumns, UpdateDBColumn, refetchDBColumns
from app.handlers.configuration.emailAddress_handler import fetchAllEmailAddress, UpdateEmailDetail
from app.handlers.configuration.vwAtKWE_handler import fetchAllEmployees
from app.handlers.configuration.groupEmail_handler import fetchAllGroupEmail, createNewGroup, editGroup
from app.handlers.configuration.groupMember_handler import fetchAllGroupMembers, addGroupMember, deleteMember
from app.handlers.configuration.ticketCateg_handler import fetchAllTicketCateg, createTicketCateg

config_bp = Blueprint("config", __name__)

#TESTING API
config_bp.route("/test", methods=["GET"])(testing)

#USER API
config_bp.route("/getUserProfile/<id>", methods=["GET"])(fetchUser)


#GET HRIS EMPLOYEES
config_bp.route("/getHREmp", methods=["GET"])(fetchAllEmployees)


#SYSTEM PROFILE API
config_bp.route("/getSystems", methods=["GET"])(fetchAllSystems)
config_bp.route("/CreateSystemPro", methods=["POST"])(createNewProfile)
config_bp.route("/UpdateSystemPro", methods=["PUT"])(updateProfile) 

#DB COLUMNS API
config_bp.route("/getDbColumns/<sa>", methods=["GET"])(fetchAllDBColumns)
config_bp.route("/dbcolUpd/<id>", methods=["PUT"])(UpdateDBColumn)
config_bp.route("/dbColRefetch/<sa>", methods=["POST"])(refetchDBColumns)


#EMAIL ADDRESS COLUMNS API
config_bp.route("/getEmailAddress", methods=["GET"])(fetchAllEmailAddress)
config_bp.route("/updEmail/<id>", methods=["PUT"])(UpdateEmailDetail)


#GROUP EMAIL ADDRESS
config_bp.route("/getGroupEmails", methods=["GET"])(fetchAllGroupEmail) 
config_bp.route("/CreateGroupEmail", methods=["POST"])(createNewGroup) 
config_bp.route("/UpdGroupEmail", methods=["PUT"])(editGroup) 
config_bp.route("/getGroupMember/<ge>", methods=["GET"])(fetchAllGroupMembers)
config_bp.route("/CreateGroupMember", methods=["POST"])(addGroupMember)
config_bp.route("/delMember/<id>", methods=["DELETE"])(deleteMember)

#TICKET CATEGORIES
config_bp.route("/getTicketCateg", methods=["GET"])(fetchAllTicketCateg) 
config_bp.route("/createTicketCateg", methods=["POST"])(createTicketCateg)

