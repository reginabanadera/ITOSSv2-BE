from database import db
from datetime import datetime, timedelta, date
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class EquipmentInv(db.Model):
    __tablename__ = "tblInvEquipment"
    SystemId = db.Column(db.Integer, primary_key=True)
    EmployeeId = db.Column(db.String(20), nullable=False)
    EqType = db.Column(db.String(70), nullable=False)
    Brand = db.Column(db.String(50), nullable=False)
    Model = db.Column(db.String(50), nullable=False)
    SerialNumber = db.Column(db.String(50), nullable=False)
    AssetTag = db.Column(db.String(50), nullable=True)
    Batch = db.Column(db.String(50), nullable=True)
    Year_Acquired = db.Column(db.String(50), nullable=True)
    Year_Issued = db.Column(db.String(50), nullable=True)
    EndofWarranty = db.Column(db.String(50), nullable=True)
    ForReplacementYear = db.Column(db.String(50), nullable=True)
    Remarks = db.Column(db.String(300), nullable=True)
    Added_By = db.Column(db.String(90), nullable=True)
    Modified_By = db.Column(db.String(90), nullable=True)
    Date_Modified = db.Column(db.DateTime, nullable=True)
    AccountedTo = db.Column(db.String(50), nullable=True)
    Others = db.Column(db.String(200), nullable=True)
    IRTransaction_Number = db.Column(db.String(50), nullable=True)
    Storage = db.Column(db.String(20), nullable=True)
    Memory = db.Column(db.String(70), nullable=True)
    Processor = db.Column(db.String(20), nullable=True)
    OS = db.Column(db.String(70), nullable=True)
                   
    def __init__ (self, EmployeeId, EqType, Model, Brand, SerialNumber, Added_By, **kwargs):
        self.EmployeeId = EmployeeId
        self.EqType = EqType
        self.Model = Model
        self.Brand = Brand
        self.EqType = EqType
        self.SerialNumber = SerialNumber
        self.Added_By = Added_By

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "EmployeeId": self.EmployeeId,
            "EqType": self.EqType,
            "Model": self.Model,
            "Brand": self.Brand,
            "SerialNumber": self.SerialNumber,
            "AssetTag": self.AssetTag,
            "Batch": self.Batch,
            "Year_Acquired": self.Year_Acquired,
            "Year_Issued": self.Year_Issued,
            "EndofWarranty": self.EndofWarranty,
            "ForReplacementYear": self.ForReplacementYear,
            "Remarks": self.Remarks,
            "Added_By": self.Added_By,
            "Modified_By": self.Modified_By,
            "Date_Modified": self.Date_Modified,
            "AccountedTo": self.AccountedTo,
            "Others": self.Others,
            "IRTransaction_Number": self.IRTransaction_Number,
            "Storage": self.Storage,
            "Memory": self.Memory,
            "Processor": self.Processor,
            "OS": self.OS
        }


    
