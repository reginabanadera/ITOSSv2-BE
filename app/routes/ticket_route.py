from flask import Blueprint
from app.handlers.ticketing.ticketing_handler import createTicket, update_Ticket, fetchTickets, get_DBColumns, createTicket_message, resendTicket, cancelRequest, assignTicket, confirmAssignedTicket, processInhouse, generateFile, ticketServiceNow, ticketClose
from app.handlers.ticketing.approval_handler import approval_history, approveTicket, declineTicket

tick_bp = Blueprint("ticket", __name__)


tick_bp.route("/ticket", methods=["POST"])(createTicket)
tick_bp.route("/ticket", methods=["PUT"])(update_Ticket)
tick_bp.route("/ticket", methods=["GET"])(fetchTickets)
tick_bp.route("/systems/<system_key>/modules", methods=["GET"])(get_DBColumns)
tick_bp.route("/message", methods=["POST"])(createTicket_message)
tick_bp.route("/re-send", methods=["POST"])(resendTicket)
tick_bp.route("/cancel", methods=["POST"])(cancelRequest)
tick_bp.route("/assign", methods=["POST"])(assignTicket)
tick_bp.route("/confirmassign", methods=["POST"])(confirmAssignedTicket)
tick_bp.route("/process", methods=["POST"])(processInhouse)
tick_bp.route("/<ticket_id>/generateFile", methods=["POST"])(generateFile)
tick_bp.route("/ticket/close", methods=["POST"])(ticketClose)
tick_bp.route("/ticket/serviceNow", methods=["POST"])(ticketServiceNow)


tick_bp.route("/getapprovalhist", methods=["GET"])(approval_history)
tick_bp.route("/approve", methods=["POST"])(approveTicket)
tick_bp.route("/decline", methods=["POST"])(declineTicket)