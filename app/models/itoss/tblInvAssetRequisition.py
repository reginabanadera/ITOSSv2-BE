from database import db
from datetime import datetime, timedelta, date
import pytz

philippines_tz = pytz.timezone('Asia/Manila')

class AssetRequisition(db.Model):
    __tablename__ = 'tblInvAssetRequisition'
    SystemId = db.Column(db.Integer, primary_key=True)
    SerialNumber = db.Column(db.String(50), nullable=False)
    AssetTag = db.Column(db.String(50), nullable=True)
    Existing = db.Column(db.Integer, nullable=False)
    Model = db.Column(db.String(100), nullable=False)
    Brand = db.Column(db.String(100), nullable=False)
    EType = db.Column(db.String(100), nullable=False)
    Tagged = db.Column(db.Integer, nullable=False)
    Company = db.Column(db.String(100), nullable=False)
    ItemDescription = db.Column(db.String(100), nullable=True)
    Classification = db.Column(db.String(50), nullable=True)
    AccountName = db.Column(db.String(50), nullable=True)
    Cost = db.Column(db.String(20), nullable=True)
    DateAcquired = db.Column(db.Date, nullable=True)
    Assigned = db.Column(db.Integer, nullable=True)
    EndofWarranty = db.Column(db.String(50), nullable=True)
    DateChecked = db.Column(db.Date, nullable=True)
    AddedBy = db.Column(db.String(90), nullable=False)
    DateAdded = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    ModifiedBy = db.Column(db.String(80), nullable=True)
    DateModified = db.Column(db.DateTime, nullable=True)

    def __init__ (self, SerialNumber, Existing, Model, Brand, EType, Tagged, Company, AddedBy, **kwargs):
        self.SerialNumber = SerialNumber
        self.Existing = Existing
        self.Model = Model
        self.Brand = Brand
        self.EType = EType
        self.Tagged = Tagged
        self.Company = Company
        self.AddedBy = AddedBy


        for key, value in kwargs.items():
            setattr(self, key, value)


    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "SerialNumber": self.SerialNumber,
            "AssetTag": self.AssetTag,
            "Existing": self.Existing,
            "Model": self.Model,
            "Brand": self.Brand,
            "EType": self.EType,
            "Tagged": self.Tagged,
            "Company": self.Company,
            "ItemDescription": self.ItemDescription,
            "Classification": self.Classification,
            "AccountName": self.AccountName,
            "Cost": self.Cost,
            "DateAcquired": self.DateAcquired,
            "EndofWarranty": self.EndofWarranty,
            "Assigned": self.Assigned,
            "DateChecked":self.DateChecked,
            "AddedBy": self.AddedBy,
            "DateAdded": self.DateAdded,
            "ModifiedBy": self.ModifiedBy,
            "DateModified": self.DateModified
        }
