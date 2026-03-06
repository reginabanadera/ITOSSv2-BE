from database import db
from app.models.itoss.tblConfigGroupEmails import GroupEmails
from datetime import datetime, timedelta
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class GroupMembers(db.Model):
    __tablename__ = 'tblConfigGroupMembers'
    SystemId = db.Column(db.Integer, primary_key=True)
    GroupEmail = db.Column(db.String(90), db.ForeignKey(GroupEmails.GroupEmail), nullable=False)
    EmailAddress = db.Column(db.String(90), nullable=False)
    EmployeeId = db.Column(db.String(10), nullable=False)
    Type = db.Column(db.String(50), nullable=False)
    DateAdded = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    Added_By = db.Column(db.String(60), nullable=False)
    Modified_By = db.Column(db.String(80), nullable=True)
    Date_Modified = db.Column(db.Date, nullable=True)

    def __init__ (self, GroupEmail, EmailAddress, EmployeeId, Type, Added_By, **kwargs):
        self.GroupEmail = GroupEmail
        self.EmailAddress = EmailAddress
        self.EmployeeId = EmployeeId
        self.Type = Type
        self.Added_By = Added_By

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "GroupEmail": self.GroupEmail,
            "EmailAddress": self.EmailAddress,
            "EmployeeId": self.EmployeeId,
            "Type": self.Type,
            "DateAdded": self.DateAdded,
            "Added_By": self.Added_By,
            "Modified_By": self.Modified_By,
            "Date_Modified": self.Date_Modified,
        }