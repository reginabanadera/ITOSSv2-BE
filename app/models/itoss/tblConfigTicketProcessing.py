from database import db
from datetime import datetime
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy import JSON  # Optional if your DB supports JSON natively
import pytz
import json

philippines_tz = pytz.timezone('Asia/Manila')

class TicketProcessing(db.Model):
    __tablename__ = 'tblConfigTicketProcessing'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    CategoryId = db.Column(
        db.Integer,
        db.ForeignKey('dbo.tblConfigTicketCategories.SystemId'),
        nullable=False
    )
    
    FieldName = db.Column(db.String(50), nullable=False)
    FieldType = db.Column(db.String(50), nullable=False)
    FieldLabel = db.Column(db.String(50), nullable=False)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(50), nullable=True)
    
    def __init__ (self, CategoryId, FieldName, FieldType, FieldLabel, CreatedBy, **kwargs):
        self.CategoryId = CategoryId
        self.FieldName = FieldName
        self.FieldType = FieldType
        self.FieldLabel = FieldLabel
        self.CreatedBy = CreatedBy
       
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "CategoryId": self.CategoryId,
            "FieldName": self.FieldName,
            "FieldType": self.FieldType,
            "FieldLabel": self.FieldLabel,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
        }
