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


class TicketSnaphot(db.Model):
    __tablename__ = 'tblTransTicketSnapshot'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(db.String(50), nullable=False)
    RequestTypeCode = db.Column(db.Integer, nullable=False)
    ApprovalFlow = db.Column(db.Text, nullable=False)
    FormSchema = db.Column(db.Text, nullable=False)


    def __init__ (self, TicketNumber, RequestTypeCode, ApprovalFlow, FormSchema):
        self.TicketNumber = TicketNumber
        self.RequestTypeCode = RequestTypeCode
        self.ApprovalFlow = ApprovalFlow
        self.FormSchema = FormSchema

    
    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "RequestTypeCode": self.RequestTypeCode,
            "ApprovalFlow": self.ApprovalFlow,
            "FormSchema": self.FormSchema,
        }
