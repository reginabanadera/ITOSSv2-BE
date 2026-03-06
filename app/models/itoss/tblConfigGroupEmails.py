from database import db
from datetime import datetime, timedelta
import pytz

philippines_tz = pytz.timezone('Asia/Manila')


class GroupEmails(db.Model):
    __tablename__ = 'tblConfigGroupEmail'
    SystemId = db.Column(db.Integer, primary_key=True)
    GroupName = db.Column(db.String(80), nullable=False)
    GroupEmail = db.Column(db.String(80), nullable=False, unique=True)
    DateAdded = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    Added_By = db.Column(db.String(60), nullable=False)
    Status = db.Column(db.String(1), nullable=False)
    Modified_By = db.Column(db.String(80), nullable=True)
    Date_Modified = db.Column(db.Date, nullable=True)

    def __init__ (self, GroupName, GroupEmail, Added_By, Status, **kwargs):
        self.GroupName = GroupName
        self.GroupEmail = GroupEmail
        self.Added_By = Added_By
        self.Status = Status

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "GroupName": self.GroupName,
            "GroupEmail": self.GroupEmail,
            "DateAdded": self.DateAdded,
            "Added_By": self.Added_By,
            "Status": self.Status,
            "Modified_By": self.Modified_By,
            "Date_Modified": self.Date_Modified,
        }