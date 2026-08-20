from database import db
from datetime import datetime
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class TicketServiceNow(db.Model):
    __tablename__ = 'tblTransTicketServiceNow'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    RequestType = db.Column(db.String(50), nullable=False)
    TicketNumber = db.Column(
        db.String(50),
        db.ForeignKey('dbo.tblTransTickets.TicketNumber'),
        nullable=False
    )
    SNIncidentNumber = db.Column(db.String(50), nullable=False)
    DateStarted = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    DateFinished = db.Column(db.DateTime, nullable=False)
    Status = db.Column(db.String(15), nullable=False)

    def __init__ (self, RequestType, TicketNumber, SNIncidentNumber, DateStarted, Status):
        self.RequestType = RequestType
        self.TicketNumber = TicketNumber
        self.SNIncidentNumber = SNIncidentNumber
        self.DateStarted = DateStarted
        self.Status = Status


    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "RequestType": self.RequestType,
            "TicketNumber": self.TicketNumber,
            "SNIncidentNumber": self.SNIncidentNumber,
            "DateStarted": self.DateStarted.isoformat() if self.DateStarted else None,
            "Status": self.Status,
            "DateFinished": self.DateFinished.isoformat() if self.DateFinished else None,
        }
