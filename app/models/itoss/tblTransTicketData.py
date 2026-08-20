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


class TicketData(db.Model):
    __tablename__ = 'tblTransTicketData'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(
        db.String(50),
        db.ForeignKey('dbo.tblTransTickets.TicketNumber'),
        nullable=False
    )
    CustomFields = db.Column(db.Text, nullable=False)
   
    def __init__ (self, TicketNumber, CustomFields):
        self.TicketNumber = TicketNumber
        self.CustomFields = CustomFields

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "CustomFields": parse_static_options(self.CustomFields) if self.CustomFields else [],
        }
