from database import db
from datetime import datetime
import pytz
import json

philippines_tz = pytz.timezone('Asia/Manila')

class TicketMessage(db.Model):
    __tablename__ = 'tblTransTicketMessage'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(
        db.String(50),
        db.ForeignKey('dbo.tblTransTickets.TicketNumber'),
        nullable=False
    )
    EmployeeId = db.Column(db.String(20), nullable=False)
    SenderName = db.Column(db.String(90), nullable=False)
    Message = db.Column(db.Text, nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))

    files = db.relationship(
        "TicketMessageFile",
        backref="message",
        lazy=True
    )

    def __init__ (self, TicketNumber, EmployeeId, SenderName, Message, **kwargs):
        self.TicketNumber = TicketNumber
        self.EmployeeId = EmployeeId
        self.SenderName = SenderName
        self.Message = Message

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "EmployeeId": self.EmployeeId,
            "SenderName": self.SenderName,
            "Message": self.Message,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
        }
