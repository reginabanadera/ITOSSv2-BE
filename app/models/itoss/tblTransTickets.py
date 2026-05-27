from database import db
from datetime import datetime
import pytz
import json

philippines_tz = pytz.timezone('Asia/Manila')

def parse_static_options(value):
    try:
        result = json.loads(value)

        # If still string → decode again
        if isinstance(result, str):
            result = json.loads(result)

        return result
    except Exception:
        return []


class Tickets(db.Model):
    __tablename__ = 'tblTransTickets'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(db.String(50), nullable=False)
    RequestType = db.Column(db.Integer, db.ForeignKey('dbo.tblConfigTicketCategories.SystemId'), nullable=False)
    RequestorId = db.Column(db.String(50), nullable=False)
    RequestFor = db.Column(db.String(50), nullable=False)
    Status = db.Column(db.String(50), nullable=False)
    CurrentLevel = db.Column(db.Integer, nullable=False)
    DHId = db.Column(db.String(50), nullable=False)
    ISId = db.Column(db.String(50), nullable=False)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    DateModified = db.Column(db.DateTime, nullable=True)
    
    request_name = db.relationship(
        "TicketCategory",
        backref="tickets",
        lazy=True,
        uselist=False  # 🔥 important
    )

    approvers = db.relationship(
        "TicketApproval",
        backref="category",
        lazy=True
    )

    custom_fields = db.relationship(
        "TicketData",
        backref="data",
        lazy=True
    )

    messages = db.relationship(
        "TicketMessage",
        backref="message",
        lazy=True
    )

    def __init__ (self, TicketNumber, RequestType, RequestorId, RequestFor, Status, CurrentLevel, DHId, ISId):
        self.TicketNumber = TicketNumber
        self.RequestType = RequestType
        self.RequestorId = RequestorId
        self.RequestFor = RequestFor
        self.Status = Status
        self.CurrentLevel = CurrentLevel
        self.DHId = DHId
        self.ISId = ISId

    
    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "RequestorId": self.RequestorId,
            "RequestFor": self.RequestFor,
            "RequestType": self.RequestType,
            "RequestName": self.request_name.Name if self.request_name else None,
            "approvers": [
                {   
                    "ApprovalLevel": a.ApprovalLevel,
                    "ApproverId": a.ApproverId,
                    "Action": a.Action,
                    "Remarks": a.Remarks,
                    "DateActed": a.DateActed.isoformat() if a.DateActed else None,
                }
                for a in self.approvers
            ],
            "custom_fields" : [
                {
                    "CustomFields": parse_static_options(c.CustomFields) if c.CustomFields else [],
                }
                for c in self.custom_fields
            ],

            "messages" : [
                {
                    "Sender": m.EmployeeId,
                    "SenderName": m.SenderName,
                    "Message": m.Message,
                    "Status": m.Status,
                    "DateSent": m.DateCreated.isoformat() if m.DateCreated else None,
                }
                for m in self.messages
            ],
            "Status": self.Status,
            "CurrentLevel": self.CurrentLevel,
            "DHId": self.DHId,
            "ISId": self.ISId,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "DateModified": self.DateModified.isoformat() if self.DateModified else None,   
        }
