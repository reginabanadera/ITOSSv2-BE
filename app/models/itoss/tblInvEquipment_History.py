from database import db
from datetime import datetime, timedelta, date
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class InvEquipment_History(db.Model):
    __tablename__ = 'tblInvEquipment_History'
    SystemId = db.Column(db.Integer, primary_key=True)
    EmployeeId = db.Column(db.String(50), nullable=False)
    EType = db.Column(db.String(50), nullable=False)
    AssetTag = db.Column(db.String(50), nullable=False)
    SerialNumber = db.Column(db.String(50), nullable=False)
    Model = db.Column(db.String(100), nullable=False)
    Brand = db.Column(db.String(100), nullable=False)
    Added_By = db.Column(db.String(90), nullable=False)
    Date_Added = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    AccountedTo = db.Column(db.String(50), nullable=False)
    
    def __init__ (self, EmployeeId, EType, AssetTag, SerialNumber, Model, Brand, Added_By, AccountedTo):
        self.EmployeeId = EmployeeId
        self.EType = EType
        self.AssetTag = AssetTag
        self.SerialNumber = SerialNumber
        self.Model = Model
        self.Brand = Brand
        self.Added_By = Added_By
        self.AccountedTo = AccountedTo

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "EmployeeId": self.EmployeeId,
            "EType": self.EType,
            "AssetTag": self.AssetTag,
            "SerialNumber": self.SerialNumber,
            "Model": self.Model,
            "Brand": self.Brand,
            "AccountedTo": self.AccountedTo
        }
           