from database import db
from datetime import datetime, timedelta
import pytz

philippines_tz = pytz.timezone('Asia/Manila')


class EmailAddress(db.Model):
    __tablename__ = 'tblConfigEmailAddress'
    SystemId = db.Column(db.Integer, primary_key=True)
    EmployeeId = db.Column(db.String(60), nullable=False)
    EmailAddress = db.Column(db.String(80), nullable=False)
    DateAdded = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    Added_By = db.Column(db.String(60), nullable=False)
    Date_Created = db.Column(db.Date, nullable=True)
    Date_Deleted = db.Column(db.Date, nullable=True)
    Status = db.Column(db.String(20), nullable=False)
    Modified_By = db.Column(db.String(80), nullable=True)
    Date_Modified = db.Column(db.Date, nullable=True)

    def __init__ (self, EmployeeId, EmailAddress, DateAdded, Added_By, Date_Created, Status, **kwargs):
        self.EmployeeId = EmployeeId
        self.EmailAddress = EmailAddress
        self.DateAdded = DateAdded
        self.Added_By = Added_By
        self.Date_Created = Date_Created
        self.Status = Status

        for key, value in kwargs.items():
            setattr(self, key, value)


    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "EmployeeId": self.EmployeeId,
            "EmailAddress": self.EmailAddress,
            "DateAdded": self.DateAdded,
            "Added_By": self.Added_By,
            "Date_Created": self.Date_Created,
            "Date_Deleted": self.Date_Deleted,
            "Status": self.Status,
            "Modified_By": self.Modified_By,
            "Date_Modified": self.Date_Modified,
        }
