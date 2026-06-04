from database import db
from app.models.itoss.tblTransApprovalLevel import TicketApproval
from app.models.itoss.tblConfigTicketCategApprover import TicketApproverLevel
from app.models.itoss.tblTransTickets import Tickets
from app.models.itoss.tblTransTicketMessage import TicketMessage
from flask import jsonify, request, g
from app.services.jwt_validator import token_required

@token_required
def approval_history():
    approvals = TicketApproval.query.all()
    if not approvals:
            return jsonify({"error": "No approvals found"}), 404  # Not Found is more appropriate

    return jsonify([approval.to_dict() for approval in approvals]), 200

@token_required
def approveTicket():
    try:
        data = request.get_json()

        ticketno = data.get("TicketNumber")
        currentLevel = data.get("CurrentLevel")
        requestType = data.get("RequestType")

        nextLevel = currentLevel + 1
        current_user = g.payload["emp_id"]
        current_username = g.payload["username"]


        approve = Tickets.query.filter(Tickets.TicketNumber == ticketno).first()
        if not approve: 
            return jsonify({"message": "No ticket number found!"}), 404

        config = TicketApproverLevel.query.filter(
            TicketApproverLevel.CategoryId == requestType,
            TicketApproverLevel.LevelNo == nextLevel
        ).first()

        if not config:
            return jsonify({"message": "Approver level configuration not found!"}), 404

        approve.CurrentLevel = config.LevelNo
        approve.Status = config.Description

        #------------------APPROVAL HISTORY----------------------
        new_history = TicketApproval(
            TicketNumber = ticketno,
            ApprovalLevel= nextLevel,
            ApproverId = current_user,
            Action = config.Description,
            Remarks = config.Description
        )

        db.session.add(new_history)

        #------------------MESSAGE-------------------------------
        remarks = f"Approved {ticketno}"
        new_message = TicketMessage(
            TicketNumber=ticketno,
            EmployeeId=current_user,
            SenderName=current_username,
            Status=config.Description,
            Message=remarks
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({"message": "Request successfully approved!"}), 200
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR APPROVING TICKET ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500
    
@token_required
def declineTicket():
    try:
        data = request.get_json()

        ticketno = data.get("TicketNumber")
        reason = data.get("reason")

        current_user = g.payload["emp_id"]
        current_username = g.payload["username"]


        approve = Tickets.query.filter(Tickets.TicketNumber == ticketno).first()
        if not approve: 
            return jsonify({"message": "No ticket number found!"}), 404

        Status = "Declined"

        approve.CurrentLevel =  0
        approve.Status = Status

        #------------------APPROVAL HISTORY----------------------
        new_history = TicketApproval(
            TicketNumber = ticketno,
            ApprovalLevel= 0,
            ApproverId = current_user,
            Action = Status,
            Remarks = reason
        )

        db.session.add(new_history)

        #------------------MESSAGE-------------------------------
        remarks = f"Declined {ticketno}: {reason}"
        new_message = TicketMessage(
            TicketNumber=ticketno,
            EmployeeId=current_user,
            SenderName=current_username,
            Status=Status,
            Message=remarks
        )

        db.session.add(new_message)
        db.session.commit()

        return jsonify({"message": "Request successfully declined!"}), 200
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR DECLINING TICKET ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500