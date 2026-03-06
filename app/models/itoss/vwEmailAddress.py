from database import db
from datetime import datetime, timedelta
import pytz

philippines_tz = pytz.timezone('Asia/Manila')


class vwEmailAddress(db.Model):
    __tablename__ = 'vwEmailAddress'
    SystemId = db.Column(db.Integer, primary_key=True)
    EmployeeId = db.Column(db.String(20))
    FullName = db.Column(db.String(70))
    EmailAddress = db.Column(db.String(80))
    Department = db.Column(db.String(300))
    DateAdded = db.Column(db.DateTime)
    Added_By = db.Column(db.String(60))
    Date_Created = db.Column(db.Date)
    DateResigned = db.Column(db.Date)
    Date_Deleted = db.Column(db.Date)
    Status = db.Column(db.String(20))
    Modified_By = db.Column(db.String(80))
    Date_Modified = db.Column(db.Date)

    
    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "EmployeeId": self.EmployeeId,
            "FullName": self.FullName,
            "EmailAddress": self.EmailAddress,
            "Department": self.Department,
            "DateAdded": self.DateAdded,
            "Added_By": self.Added_By,
            "Date_Created": self.Date_Created,
            "DateResigned": self.DateResigned,
            "Date_Deleted": self.Date_Deleted,
            "Status": self.Status,
            "Modified_By": self.Modified_By,
            "Date_Modified": self.Date_Modified,
        }
