from database import db
from datetime import datetime
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class TicketMessageFile(db.Model):
    __tablename__ = 'tblTransTicketMessageFile'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    TicketNumber = db.Column(
        db.String(50),
        db.ForeignKey('dbo.tblTransTickets.TicketNumber'),
        nullable=False
    )
    MessageId = db.Column(
        db.Integer,
        db.ForeignKey('dbo.tblTransTicketMessage.SystemId'),
        nullable=False
    )
    FileName = db.Column(db.String(100), nullable=False)
    FilePath = db.Column(db.String(300), nullable=False)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))

    def __init__ (self, TicketNumber, MessageId, FileName, FilePath, **kwargs):
        self.TicketNumber = TicketNumber
        self.MessageId = MessageId
        self.FileName = FileName
        self.FilePath = FilePath

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "TicketNumber": self.TicketNumber,
            "MessageId": self.MessageId,
            "FileName": self.FileName,
            "FilePath": self.FilePath,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
        }
