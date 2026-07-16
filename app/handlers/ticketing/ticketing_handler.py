import os
from database import db
from flask import current_app
from sqlalchemy import text
from app.models.itoss.tblTransTickets import Tickets
from app.models.itoss.tblTransTicketData import TicketData
from app.models.itoss.tblTransApprovalLevel import TicketApproval
from app.models.itoss.tblConfigTicketCategApprover import TicketApproverLevel
from app.models.itoss.tblTransTicketSnapshot import TicketSnaphot
from app.models.itoss.tblTransTicketInhouseModule import TicketInhouseModule
from app.models.itoss.tblTransTicketMessage import TicketMessage
from app.models.itoss.tblTransTicketMessageFile import TicketMessageFile
from app.models.hris.vwDeptHead import vwDeptHead
from app.models.hris.vwAtKWE import vwAtKWE
from app.services.mfa_registration import check_mfa
from app.services.email_sending import send_email
from app.services.inhouse_process import process_access
from flask import jsonify, request, g
from werkzeug.utils import secure_filename
from app.services.jwt_validator import token_required
from datetime import datetime
import pytz
import json
from sqlalchemy import or_

# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)

# Format to YYYY-MM-DD
formatted_date = now_ph.strftime("%Y-%m-%d")

formatted_datentime = now_ph.strftime("%Y-%m-%d %H:%M:%S")

UPLOAD_FOLDER = "./app/uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "pdf", "xls", "xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def fetchTickets():
    try:
        requestor = request.args.get("requestor")
        status = request.args.get("status")
        status_view = request.args.get("status_view")
        ticketno = request.args.get("ticketno")

        query = Tickets.query

        if requestor:
            query = query.filter(Tickets.RequestorId == requestor)
        if status:
            query = query.filter(Tickets.Status == status)
        if status_view and status_view == "open":
            approved = Tickets.Status.ilike("%Approved%")
            submitted = Tickets.Status.ilike("%Submitted%")
            processing = Tickets.Status == "For Processing"

            query = query.filter(or_(approved, submitted, processing))
        if ticketno: 
            query = query.filter(Tickets.TicketNumber == ticketno)

        query = query.order_by(Tickets.DateCreated.desc())

        tickets = query.all()

        # 🔥 ENRICH USERS (cross-db safe way)
         # 🔥 ENRICH USERS (Requestor + RequestFor)
        user_ids = list({
            t.RequestorId for t in tickets
        } | {
            t.RequestFor for t in tickets
        })

        users = vwAtKWE.query.filter(
            vwAtKWE.EmployeeId.in_(user_ids)
        ).all()

        user_map = {u.EmployeeId: u.FullName for u in users}

        result = []
        for t in tickets:
            data = t.to_dict()
            data["RequestorName"] = user_map.get(t.RequestorId)
            data["RequestForName"] = user_map.get(t.RequestFor)
            result.append(data)

        return jsonify(result), 200

    except Exception as e:
        import traceback
        print("=== ERROR CREATING TICKET ===")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



def generate_transaction_no():
    today = datetime.now().strftime("%Y%m%d")

    # Get latest ticket today
    last_ticket = Tickets.query.filter(
        Tickets.TicketNumber.like(f"TKT-{today}%")
    ).order_by(Tickets.TicketNumber.desc()).first()

    if last_ticket:
        last_number = int(last_ticket.TicketNumber.split("-")[-1])
        new_number = last_number + 1
    else:
        new_number = 1

    return f"TKT-{today}-{new_number:04d}"

@token_required
def createTicket():
    try:

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        ticket_no = generate_transaction_no()

        RequestFor = request.form.get("RequestFor")
        EmailAdd = request.form.get("emailaddress")
        RequestType = request.form.get("Category")

        current_user = g.payload['emp_id']
        current_username = g.payload['username']

        status = "Submitted"

        DHId = request.form.get("DHId")
        ISId = request.form.get("ISId")

        systemName = request.form.get("system_name")

        CustomFields = json.loads(
            request.form.get("custom_fields", "{}")
        )

        modules = json.loads(
            request.form.get("modules", "[]")
        )

        # ---------------- FILE HANDLING ----------------

        uploaded_file_data = {}

        for key in request.files:

            uploaded_files = request.files.getlist(key)

            saved_files = []

            for file in uploaded_files:

                if file and file.filename:

                    filename = secure_filename(file.filename)

                    unique_filename = f"{ticket_no}_{filename}"

                    save_path = os.path.join(
                        UPLOAD_FOLDER,
                        unique_filename
                    )

                    # SAVE ACTUAL FILE
                    file.save(save_path)

                    # SAVE FILE INFO
                    saved_files.append({
                        "filename": filename,
                        "stored_filename": unique_filename,
                        "path": save_path,
                        "content_type": file.content_type
                    })

            # SAVE TO CUSTOM FIELDS
            if saved_files:
                uploaded_file_data[key] = saved_files

        CustomFields.update(uploaded_file_data)

        # ---------------- EXTRA CUSTOM FIELD ----------------

        if systemName:
            CustomFields["SystemName"] = systemName

        # ---------------- DUPLICATE CHECK ----------------

        ticket = Tickets.query.filter(
            Tickets.RequestFor == RequestFor,
            Tickets.Status == "Submitted",
            Tickets.RequestType == RequestType
        ).first()

        if ticket:
            return {"message": "Record already exists."}, 400

        # ---------------- APPROVAL FLOW ----------------

        configs = (
            TicketApproverLevel.query
            .filter_by(CategoryId=RequestType)
            .order_by(TicketApproverLevel.LevelNo)
            .all()
        )

        current_level = 1

        approval_flow = []

        for cfg in configs:

            approval_flow.append({
                "level": cfg.LevelNo,
                "approverType": cfg.ApproverType,
                "ApproverValue": cfg.ApproverValue,
            })

        
            # SELF REQUEST + DH
            if (
                RequestFor == current_user and
                cfg.ApproverType == "Dynamic Manager"
            ):

                is_dh = vwDeptHead.query.filter_by(
                    EmployeeId=RequestFor
                ).first()

                if is_dh:
                    status = cfg.Description
                    current_level = cfg.LevelNo
                    break

            # DYNAMIC SUPERIOR
            elif cfg.ApproverType == "Dynamic Superior":

                if ISId == current_user:
                    status = cfg.Description
                    current_level = cfg.LevelNo
                    break

            elif cfg.ApproverType == "Dynamic Manager":
                if DHId == current_user:
                    status = cfg.Description
                    current_level = cfg.LevelNo
                    break
            
            # SPECIFIC USER
            elif cfg.ApproverType == "Specific User":

                if (current_user == cfg.ApproverValue):
                    status = cfg.Description
                    current_level = cfg.LevelNo
                    break

        # ---------------- CREATE TICKET ----------------

        new_ticket = Tickets(
            TicketNumber=ticket_no,
            RequestFor=RequestFor,
            RequestorId=current_user,
            RequestType=RequestType,
            Status=status,
            CurrentLevel=current_level,
            DHId=DHId,
            ISId=ISId
        )

        db.session.add(new_ticket)

        # ---------------- TICKET DATA ----------------

        new_ticketData = TicketData(
            TicketNumber=ticket_no,
            CustomFields=json.dumps(CustomFields)
        )

        db.session.add(new_ticketData)

        # ---------------- APPROVAL ----------------

        new_approval = TicketApproval(
            TicketNumber=ticket_no,
            ApprovalLevel=current_level,
            ApproverId=current_user,
            Action=status,
            Remarks=status
        )

        db.session.add(new_approval)

        # ---------------- MODULES ----------------

        for md in modules:

            new_module = TicketInhouseModule(
                TicketNumber=ticket_no,
                EmployeeId=RequestFor,
                EmailAddress=EmailAdd,
                Inhouse=systemName,
                ModuleName=md
            )

            db.session.add(new_module)


        # ---------------- MESSAGE -----------------
        remarks = f"Ticket {ticket_no} created"

        new_message = TicketMessage(
            TicketNumber=ticket_no,
            EmployeeId=current_user,
            SenderName=current_username,
            Message=remarks,
            Status=status
        )

        db.session.add(new_message)

        # ---------------- SNAPSHOT ----------------

        snapshot_data = {
            "RequestorId": current_user,
            "RequestFor": RequestFor,
            "CustomFields": CustomFields,
            "Status": status
        }

        ticket_snap = TicketSnaphot(
            TicketNumber=ticket_no,
            RequestTypeCode=RequestType,
            FormSchema=json.dumps(snapshot_data),

            # FIXED: no double json.dumps
            ApprovalFlow=json.dumps(approval_flow)
        )

        db.session.add(ticket_snap)
        db.session.commit()

        # ---------------- SEND EMAIL-----------------

        NextLevel = current_level +  1

        config = TicketApproverLevel.query.filter(
                TicketApproverLevel.CategoryId==RequestType,
                TicketApproverLevel.LevelNo==NextLevel
        ).first()
        if config:
            approver = config.ApproverType
            receiver = None
            next_approver = None

            if approver == "Dynamic Manager":
                next_approver = DHId
                get_DHEmail = vwAtKWE.query.filter_by(EmployeeId = next_approver).first()
                if get_DHEmail:
                    receiver = get_DHEmail.EmailAddress
            elif approver == "Specific User":
                next_approver = config.ApproverValue
                get_Email = vwAtKWE.query.filter_by(EmployeeId = next_approver).first()
                if get_Email:
                    receiver = get_Email.EmailAddress

            if receiver:

                receiver = "reginamaye.banadera@kwe.com"
                subject = f"ITOSS For Approval [{formatted_date}]"
                html = f"""
                    <html>
                    <body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, sans-serif;">

                        <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
                        <tr>
                            <td align="center">

                            <table width="600" cellpadding="0" cellspacing="0"
                                style="background:#ffffff; border-radius:10px; overflow:hidden;">

                                <!-- Header -->
                                <tr>
                                <td style="background:#1677ff; padding:20px;">
                                    <h2 style="margin:0; color:#ffffff; font-size:18px;">
                                    IT Support Notification
                                    </h2>
                                </td>
                                </tr>

                                <!-- Content -->
                                <tr>
                                <td style="padding:25px; color:#333333; font-size:14px; line-height:1.6;">

                                    <p>Hello,</p>

                                    <p>
                                    This is an automated reminder for a pending request in the
                                    Information Technology Online Support System.
                                    </p>

                                    <!-- Request Details -->
                                    <table width="100%" cellpadding="0" cellspacing="0"
                                        style="margin:20px 0; border:1px solid #f0f0f0; border-radius:8px;">

                                        <tr>
                                            <td colspan="2"
                                                style="background:#fafafa; padding:12px 15px; font-weight:bold; font-size:14px;">
                                                Request Details
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 15px; width:35%; color:#666;">
                                                Ticket No.
                                            </td>
                                            <td style="padding:12px 15px; font-weight:600;">
                                                {ticket_no}
                                            </td>
                                        </tr>

                                        
                                        <tr>
                                            <td style="padding:12px 15px; color:#666;">
                                                Requestor Name
                                            </td>
                                            <td style="padding:12px 15px;">
                                                {current_username}
                                            </td>
                                        </tr>

                                        <tr style="background:#fcfcfc;">
                                            <td style="padding:12px 15px; color:#666;">
                                                Status
                                            </td>
                                            <td style="padding:12px 15px;">
                                                <span style="
                                                    background:#fff7e6;
                                                    color:#d48806;
                                                    padding:4px 10px;
                                                    border-radius:20px;
                                                    font-size:12px;
                                                    font-weight:bold;
                                                ">
                                                    {status}
                                                </span>
                                            </td>
                                        </tr>

                                    </table>

                                    <!-- Highlight -->
                                    <div style="
                                        background:#f5f8ff;
                                        border-left:4px solid #1677ff;
                                        padding:12px;
                                        margin:20px 0;
                                    ">
                                        Please log in to the system to review the request details.
                                    </div>

                                    <p>
                                    This is a system-generated email. Please do not reply directly
                                    to this message.
                                    </p>

                                    <br/>

                                    <p>
                                    Regards,<br/>
                                    <b>IT Support Team</b>
                                    </p>

                                </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                <td style="
                                    background:#f0f2f5;
                                    padding:15px;
                                    text-align:center;
                                    font-size:12px;
                                    color:#888;
                                ">
                                    © 2026 Information Technology Online Support System
                                </td>
                                </tr>

                            </table>

                            </td>
                        </tr>
                        </table>

                    </body>
                    </html>
                    """
                send_email(receiver, subject, html)

        return {
            "message": "Ticket created successfully",
            "ticket_no": ticket_no,
            "status": status,
            "current_level": current_level
        }, 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR CREATING TICKET ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500
    

@token_required
def update_Ticket():
    try:
        ticket_no = request.form.get("ticket_no")
        IncomingCustomFields = json.loads(
            request.form.get("custom_fields", "{}")
        )

        ticket_data = TicketData.query.filter(TicketData.TicketNumber == ticket_no).first()
        if ticket_data:
            existingCustomFields = json.loads(ticket_data.CustomFields or "{}")
            existingCustomFields.update(IncomingCustomFields)
            ticket_data.CustomFields = json.dumps(existingCustomFields)

            ticket = Tickets.query.filter(Tickets.TicketNumber == ticket_no).first()
            if ticket:
                ticket.DateModified = formatted_datentime
            
            db.session.commit()
            return jsonify({"message": "Ticket details successfully updated!"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR UPDATING TICKET ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500

@token_required
def createTicket_message():
    try:
        current_user = g.payload['emp_id']
        current_username = g.payload['username']
        # ✅ use form instead of json
        ticket_no = request.form.get("ticketno")
        mensahe = request.form.get("message")

        new_message = TicketMessage(
            TicketNumber = ticket_no,
            EmployeeId=current_user,
            SenderName=current_username,
            Message=mensahe
        )
        db.session.add(new_message)
        db.session.flush()

        files = request.files.getlist("files")

        saved_files = []

        if files:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)

            for file in files:
                if file and allowed_file(file.filename):

                    filename = secure_filename(file.filename)

                    # optional: prevent overwriting by adding message id or timestamp
                    unique_filename = f"{new_message.SystemId}_{filename}"

                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file_url = f"/uploads/{unique_filename}"

                    file.save(file_path)

                    saved_files.append(unique_filename)

                    # OPTIONAL: store in DB (recommended)
                    new_file = TicketMessageFile(
                        TicketNumber=ticket_no,
                        MessageId = new_message.SystemId,
                        FileName=unique_filename,
                        FilePath=file_url
                    )
                    db.session.add(new_file)
        
        db.session.commit()

        return jsonify({
            "message": "Message sent successfully",
            "ticket_no": ticket_no,
            "files_saved": saved_files
        }), 200
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR SENDING MESSAGE ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500
    
@token_required
def resendTicket():
    try:
        data = request.json
        ticketno = data.get('ticket_no')
        requestorName = data.get('requestorName')
        requestType = data.get('requestType')
        current_user = g.payload['emp_id']
        current_username = g.payload['username']

        ticket = Tickets.query.filter(Tickets.TicketNumber == ticketno).first()
        if ticket:
            status = ticket.Status
            category = ticket.RequestType
            NextLevel = ticket.CurrentLevel +  1

            config = TicketApproverLevel.query.filter(
                    TicketApproverLevel.CategoryId==category,
                    TicketApproverLevel.LevelNo==NextLevel
            ).first()
            if config:
                approver = config.ApproverType
                receiver = None
                next_approver = None

                if approver == "Dynamic Manager":
                    next_approver = ticket.DHId
                    get_DHEmail = vwAtKWE.query.filter_by(EmployeeId = next_approver).first()
                    if get_DHEmail:
                        receiver = get_DHEmail.EmailAddress
                elif approver == "Specific User":
                    next_approver = config.ApproverValue
                    get_Email = vwAtKWE.query.filter_by(EmployeeId = next_approver).first()
                    if get_Email:
                        receiver = get_Email.EmailAddress

            if receiver:
                mensahe = f"Sent a follow-up [{formatted_date}] to {receiver}"
                receiver = "reginamaye.banadera@kwe.com"
                subject = f"Follow-up: ITOSS For Approval [{formatted_date}]"
                html = f"""
                    <html>
                    <body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, sans-serif;">

                        <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
                        <tr>
                            <td align="center">

                            <table width="600" cellpadding="0" cellspacing="0"
                                style="background:#ffffff; border-radius:10px; overflow:hidden;">

                                <!-- Header -->
                                <tr>
                                <td style="background:#1677ff; padding:20px;">
                                    <h2 style="margin:0; color:#ffffff; font-size:18px;">
                                    IT Support Notification
                                    </h2>
                                </td>
                                </tr>

                                <!-- Content -->
                                <tr>
                                <td style="padding:25px; color:#333333; font-size:14px; line-height:1.6;">

                                    <p>Hello,</p>

                                    <p>
                                    This is an automated reminder for a pending request in the
                                    Information Technology Online Support System.
                                    </p>

                                    <!-- Request Details -->
                                    <table width="100%" cellpadding="0" cellspacing="0"
                                        style="margin:20px 0; border:1px solid #f0f0f0; border-radius:8px;">

                                        <tr>
                                            <td colspan="2"
                                                style="background:#fafafa; padding:12px 15px; font-weight:bold; font-size:14px;">
                                                Request Details
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 15px; width:35%; color:#666;">
                                                Ticket No.
                                            </td>
                                            <td style="padding:12px 15px; font-weight:600;">
                                                {ticketno}
                                            </td>
                                        </tr>

                                        <tr style="background:#fcfcfc;">
                                            <td style="padding:12px 15px; color:#666;">
                                                Request Type
                                            </td>
                                            <td style="padding:12px 15px;">
                                                {requestType}
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 15px; color:#666;">
                                                Requestor Name
                                            </td>
                                            <td style="padding:12px 15px;">
                                                {requestorName}
                                            </td>
                                        </tr>

                                        <tr style="background:#fcfcfc;">
                                            <td style="padding:12px 15px; color:#666;">
                                                Status
                                            </td>
                                            <td style="padding:12px 15px;">
                                                <span style="
                                                    background:#fff7e6;
                                                    color:#d48806;
                                                    padding:4px 10px;
                                                    border-radius:20px;
                                                    font-size:12px;
                                                    font-weight:bold;
                                                ">
                                                    {status}
                                                </span>
                                            </td>
                                        </tr>

                                    </table>

                                    <!-- Highlight -->
                                    <div style="
                                        background:#f5f8ff;
                                        border-left:4px solid #1677ff;
                                        padding:12px;
                                        margin:20px 0;
                                    ">
                                        Please log in to the system to review the request details.
                                    </div>

                                    <p>
                                    This is a system-generated email. Please do not reply directly
                                    to this message.
                                    </p>

                                    <br/>

                                    <p>
                                    Regards,<br/>
                                    <b>IT Support Team</b>
                                    </p>

                                </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                <td style="
                                    background:#f0f2f5;
                                    padding:15px;
                                    text-align:center;
                                    font-size:12px;
                                    color:#888;
                                ">
                                    © 2026 Information Technology Online Support System
                                </td>
                                </tr>

                            </table>

                            </td>
                        </tr>
                        </table>

                    </body>
                    </html>
                    """
                new_message = TicketMessage(
                    TicketNumber = ticketno,
                    EmployeeId=current_user,
                    SenderName=current_username,
                    Message=mensahe,
                    Status=status
                )
                db.session.add(new_message)
                db.session.commit()
                
                send_email(receiver, subject, html)
            return jsonify({
                "message": "Message sent successfully"
            }), 200
        
    
    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR SENDING MESSAGE ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500
    
def cancelRequest():
    try:
        data = request.json
        ticket_no = data.get("ticket_no")

        cancel = Tickets.query.filter(Tickets.TicketNumber == ticket_no).first()
        if not cancel:
            return jsonify({"message": "No ticket number found."}), 404
        
        cancel.Status = "Cancelled Request"
        cancel.DateModified = formatted_datentime
        db.session.commit()

        return jsonify({"message": "Cancellation successfull!"}), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR CANCELLING REQUEST ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500

@token_required
def assignTicket():
    try:
        data = request.json
        ticket_no = data.get("ticket_no")
        category = data.get("categoryName")
        assignedToId = data.get("assignedToId")
        assignedToName = data.get("assignedToName")
        assignedToEmail = data.get("assignedToEmail")
        status = "Assigned"
        current_user = g.payload["emp_id"]
        current_username = g.payload["username"]
        remarks = f"Assigned to {assignedToName}"

        assign = Tickets.query.filter(Tickets.TicketNumber == ticket_no).first()
        if assign:
            if assign.Status != "Assigned":
                assign.CurrentLevel = assign.CurrentLevel + 1

            assign.AssignedTo = assignedToId
            assign.DateAssigned = formatted_datentime
            assign.Status = status

            new_history = TicketApproval(
                TicketNumber = ticket_no,
                ApprovalLevel= assign.CurrentLevel + 1,
                ApproverId = current_user,
                Action = status,
                Remarks = remarks
            )
            db.session.add(new_history)

            new_message = TicketMessage(
                TicketNumber = ticket_no,
                EmployeeId=current_user,
                SenderName=current_username,
                Message=remarks,
                Status=status
            )
            db.session.add(new_message)

            db.session.commit()


            #------------------EMAIL----------------------

            subject = f"New Ticket Assigned: {ticket_no}"
            html = f"""
                    <html>
                    <body style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, sans-serif;">

                        <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;">
                        <tr>
                            <td align="center">

                            <table width="600" cellpadding="0" cellspacing="0"
                                style="background:#ffffff; border-radius:10px; overflow:hidden;">

                                <!-- Header -->
                                <tr>
                                <td style="background:#1677ff; padding:20px;">
                                    <h2 style="margin:0; color:#ffffff; font-size:18px;">
                                    IT Support Notification
                                    </h2>
                                </td>
                                </tr>

                                <!-- Content -->
                                <tr>
                                <td style="padding:25px; color:#333333; font-size:14px; line-height:1.6;">

                                    <p>Hello,</p>

                                    <p>
                                        You have been assigned a new ticket by {current_username}.
                                    </p>

                                    <!-- Request Details -->
                                    <table width="100%" cellpadding="0" cellspacing="0"
                                        style="margin:20px 0; border:1px solid #f0f0f0; border-radius:8px;">

                                        <tr>
                                            <td colspan="2"
                                                style="background:#fafafa; padding:12px 15px; font-weight:bold; font-size:14px;">
                                                Request Details
                                            </td>
                                        </tr>

                                        <tr>
                                            <td style="padding:12px 15px; width:35%; color:#666;">
                                                Ticket No.
                                            </td>
                                            <td style="padding:12px 15px; font-weight:600;">
                                                {ticket_no}
                                            </td>
                                        </tr>

                                        <tr style="background:#fcfcfc;">
                                            <td style="padding:12px 15px; color:#666;">
                                                Request Type
                                            </td>
                                            <td style="padding:12px 15px;">
                                                {category}
                                            </td>
                                        </tr>

                                        <tr style="background:#fcfcfc;">
                                            <td style="padding:12px 15px; color:#666;">
                                                Status
                                            </td>
                                            <td style="padding:12px 15px;">
                                                <span style="
                                                    background:#fff7e6;
                                                    color:#d48806;
                                                    padding:4px 10px;
                                                    border-radius:20px;
                                                    font-size:12px;
                                                    font-weight:bold;
                                                ">
                                                    {status}
                                                </span>
                                            </td>
                                        </tr>

                                    </table>

                                    <!-- Highlight -->
                                    <div style="
                                        background:#f5f8ff;
                                        border-left:4px solid #1677ff;
                                        padding:12px;
                                        margin:20px 0;
                                    ">
                                        Please log in to the system to review the request details.
                                    </div>

                                    <p>
                                    This is a system-generated email. Please do not reply directly
                                    to this message.
                                    </p>

                                    <br/>

                                    <p>
                                    Regards,<br/>
                                    <b>IT Support Team</b>
                                    </p>

                                </td>
                                </tr>

                                <!-- Footer -->
                                <tr>
                                <td style="
                                    background:#f0f2f5;
                                    padding:15px;
                                    text-align:center;
                                    font-size:12px;
                                    color:#888;
                                ">
                                    © 2026 Information Technology Online Support System
                                </td>
                                </tr>

                            </table>

                            </td>
                        </tr>
                        </table>

                    </body>
                    </html>
                    """
            send_email(assignedToEmail, subject, html)

            return jsonify({"message": "Ticket was successfully assigned!"}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR ASSIGNING REQUEST ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500

@token_required
def confirmAssignedTicket():
    try:
        data = request.json
        ticket_no = data.get("ticket_no")
        current_user = g.payload["emp_id"]
        current_username = g.payload["username"]
        status = "On Process"
        remarks = f"Confirmed the ticket assignment"

        confirm = Tickets.query.filter(Tickets.TicketNumber == ticket_no).first()
        if confirm:
            confirm.Status = "On Process"
            confirm.CurrentLevel = confirm.CurrentLevel + 1
            confirm.DateModified = formatted_datentime

            new_history = TicketApproval(
                TicketNumber = ticket_no,
                ApprovalLevel= confirm.CurrentLevel + 1,
                ApproverId = current_user,
                Action = status,
                Remarks = remarks
            )
            db.session.add(new_history)

            new_message = TicketMessage(
                TicketNumber = ticket_no,
                EmployeeId=current_user,
                SenderName=current_username,
                Message=remarks,
                Status=status
            )
            db.session.add(new_message)

            db.session.commit()

            return jsonify({"message": "Ticket assignment confirmed!"}), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR CONFIRMING ASSIGNED TICKET ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500

@token_required
def processInhouse():
    try:
        data = request.json
        ticket_no = data.get("ticket_no")
        employeeId = data.get("employeeId")
        inhouse = data.get("inhouse")
        modules = data.get("modules")
        fields_value = data.get("fieldsValue", {})
        emailAddress = None
        current_user = g.payload["emp_id"]
        current_username = g.payload["username"]
       
        if "EmailAddress" in fields_value:
            emailAddress = fields_value["EmailAddress"]

        OASId = check_mfa(employeeId, emailAddress)

        result = process_access(inhouse, employeeId, emailAddress, OASId, modules, fields_value)

        if not result["success"]:
            return jsonify(result), 400

        else:
            if result["action"] == "update":
                remarks = f"{inhouse} access has been successfully added. You may now try logging in to your account."
            else:
                remarks = (
                    f"Your {inhouse} access has been successfully added. "
                    "You may now try logging in to your account. "
                    "If you do not have a password yet or have forgotten it, you may use the 'Forgot Password' feature to set a new one. "
                    "If you already have an account in another in-house system, you can use the same password, as we are implementing a one-password-for-all approach across our in-house systems."
                )
            status = "For Closing"

            ticket = Tickets.query.filter(Tickets.TicketNumber == ticket_no).first()
            if ticket:
                ticket.Status = status
                ticket.CurrentLevel = ticket.CurrentLevel + 1
                ticket.DateModified = formatted_datentime
            
            new_history = TicketApproval(
                TicketNumber = ticket_no,
                ApprovalLevel= ticket.CurrentLevel + 1,
                ApproverId = current_user,
                Action = status,
                Remarks = remarks
            )
            db.session.add(new_history)
            
            new_message = TicketMessage(
                TicketNumber = ticket_no,
                EmployeeId=current_user,
                SenderName=current_username,
                Message=remarks,
                Status=status
            )
            db.session.add(new_message)

            db.session.commit()
            return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        print("=== ERROR PROCESSING TICKET ===")
        traceback.print_exc()
        return jsonify({
            "error": str(e)
        }), 500

def get_dynamic_superior(employee_id):
    return vwAtKWE.query.filter_by(SuperiorId=employee_id).first()


def get_dynamic_manager(employee_id):
    return vwAtKWE.query.filter(
        vwAtKWE.EmployeeId == employee_id,
        or_(
            vwAtKWE.EmpLevel.ilike("%mgr%"),
            vwAtKWE.EmpLevel.ilike("%dir%")
        )
    ).first()


def get_role_users(role):
    return vwAtKWE.query.filter_by(Designation=role).all()


def get_DBColumns(system_key):
    bind_map = current_app.config["SYSTEM_BIND_MAP"]
    
    # 🔹 1. Get system table config
    system_config = db.session.execute(text("""
        SELECT DBTableName, DBTableIdentifier
        FROM tblConfigSystemProfile
        WHERE SystemAlias = :system
    """), {"system": system_key}).fetchone()

    if not system_config:
        raise Exception("System config not found")

    table = system_config.DBTableName
    user_col = system_config.DBTableIdentifier
    bind = bind_map.get(system_key)

    # 🔹 2. Get column config
    config_rows = db.session.execute(text("""
        SELECT DBColumn, Description
        FROM tblConfigDBColumns
        WHERE SystemAlias = :system AND Description != '' AND Status = 1
    """), {"system": system_key}).fetchall()

    if not config_rows:
        return []

    column_names = [row.DBColumn for row in config_rows]
    column_sql = ", ".join(f"[{col}]" for col in column_names)

    # 🔹 3. Query target DB
    engine = db.get_engine(current_app, bind=bind)
    
    if user_col == "EmailAddress":
        user_id = request.args.get("email")
    else:
        user_id = request.args.get("userId")

    query = f"""
        SELECT {column_sql}
        FROM {table}
        WHERE {user_col} = :user_id
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {"user_id": user_id}).fetchone()

    # 🔹 4. Map response
    response = []
    for row in config_rows:
        col = row.DBColumn
        value = result._mapping.get(col, 0) if result else 0

        response.append({
            "module": col,
            "label": row.Description,
            "hasAccess": to_bool(value)
        })

    # 🔹 5. Return JSON
    return jsonify({
        "modules": response
    })


def to_bool(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return str(value).strip() in ["1", "true", "True", "Y", "yes"]



