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


class TicketInhouseModule(db.Model):
    __tablename__ = 'tblTransTicketInhouseModule'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(
        db.String(50),
        db.ForeignKey('dbo.tblTransTickets.TicketNumber'),
        nullable=False
    )
    Inhouse = db.Column(db.String(50), nullable=False)
    EmployeeId = db.Column(db.String(50), nullable=False)
    EmailAddress = db.Column(db.String(90), nullable=True)
    ModuleName = db.Column(db.String(80), nullable=False)
   
    def __init__ (self, TicketNumber, EmployeeId, ModuleName, **kwargs):
        self.TicketNumber = TicketNumber
        self.EmployeeId = EmployeeId
        self.ModuleName = ModuleName

        for key, value in kwargs.items():
            setattr(self, key, value)
        

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "EmployeeId": self.EmployeeId,
            "EmailAddress": self.EmailAddress,
            "ModuleName": self.ModuleName
        }
