from database import db
from datetime import datetime
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class TicketAssignment(db.Model):
    __tablename__ = 'tblConfigTicketAssignment'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    CategoryId = db.Column(
        db.Integer,
        db.ForeignKey('dbo.tblConfigTicketCategories.SystemId'),
        nullable=False
    )
    EmployeeId = db.Column(db.String(15), nullable=False)
    EmployeeName = db.Column(db.String(100), nullable=False)
    EmailAddress = db.Column(db.String(100), nullable=False)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(100), nullable=True)


    def __init__ (self, CategoryId, EmployeeId, EmployeeName, EmailAddress, CreatedBy, **kwargs):
        self.CategoryId = CategoryId
        self.EmployeeId = EmployeeId
        self.EmployeeName = EmployeeName
        self.EmailAddress = EmailAddress
        self.CreatedBy = CreatedBy

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "CategoryId": self.CategoryId,
            "EmployeeId": self.EmployeeId,
            "EmployeeName": self.EmployeeName,
            "EmailAddress": self.EmailAddress,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
        }


    