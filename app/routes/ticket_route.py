from flask import Blueprint
from app.handlers.ticketing.ticketing_handler import createTicket, fetchTickets, get_DBColumns, createTicket_message, resendTicket, cancelRequest

tick_bp = Blueprint("ticket", __name__)


tick_bp.route("/ticket", methods=["POST"])(createTicket)
tick_bp.route("/ticket", methods=["GET"])(fetchTickets)
tick_bp.route("/systems/<system_key>/modules", methods=["GET"])(get_DBColumns)
tick_bp.route("/message", methods=["POST"])(createTicket_message)
tick_bp.route("/re-send", methods=["POST"])(resendTicket)
tick_bp.route("/cancel", methods=["POST"])(cancelRequest)