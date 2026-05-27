from database import db
from datetime import datetime
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy import JSON  # Optional if your DB supports JSON natively
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


class TicketApproval(db.Model):
    __tablename__ = 'tblTransApprovalLevel'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(
        db.String(50),
        db.ForeignKey('dbo.tblTransTickets.TicketNumber'),
        nullable=False
    )
    ApprovalLevel = db.Column(db.Integer, nullable=False)
    ApproverId = db.Column(db.String(50), nullable=False)
    Action = db.Column(db.String(50), nullable=False)
    Remarks = db.Column(db.String(500), nullable=False)
    DateActed = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
   

    def __init__ (self, TicketNumber, ApprovalLevel, ApproverId, Action, Remarks):
        self.TicketNumber = TicketNumber
        self.ApprovalLevel = ApprovalLevel
        self.ApproverId = ApproverId
        self.Action = Action
        self.Remarks = Remarks
        

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "ApprovalLevel": self.ApprovalLevel,
            "ApproverId": self.ApproverId,
            "Action": self.Action,
            "Remarks": self.Remarks,
        }
