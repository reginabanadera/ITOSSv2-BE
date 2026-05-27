from database import db
from datetime import datetime
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy import JSON  # Optional if your DB supports JSON natively
import pytz
import json

philippines_tz = pytz.timezone('Asia/Manila')

def parse_static_options(value):
    try:
        result = json.loads(value)

        # If still string → decode again
        if isinstance(result, str):
            result = json.loads(result)

        return result
    except Exception:
        return []


class TicketCustomFields(db.Model):
    __tablename__ = 'tblConfigTicketCustomFields'
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
    IsGroup = db.Column(db.String(1), nullable=False)
    IsRepeatable = db.Column(db.String(1), nullable=False)
    GroupName = db.Column(db.String(50), nullable=False)
    ValueMode = db.Column(db.String(50), nullable=False)
    SelectSourceType = db.Column(db.String(50), nullable=True)
    SelectSourceValue = db.Column(db.String(50), nullable=True)
    TableName = db.Column(db.String(50), nullable=True)
    ValueColumn = db.Column(db.String(50), nullable=True)
    LabelColumn = db.Column(db.String(50), nullable=True)

    # NEW COLUMN for static options
    StaticOptions = db.Column(db.Text, nullable=True)  # Store JSON string of options

    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(50), nullable=True)
    
    def __init__ (self, CategoryId, FieldName, FieldType, FieldLabel, IsGroup, GroupName, ValueMode, IsRepeatable, CreatedBy, **kwargs):
        self.CategoryId = CategoryId
        self.FieldName = FieldName
        self.FieldType = FieldType
        self.CreatedBy = CreatedBy
        self.FieldLabel = FieldLabel
        self.IsGroup = IsGroup
        self.GroupName = GroupName
        self.ValueMode = ValueMode
        self.IsRepeatable = IsRepeatable

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "CategoryId": self.CategoryId,
            "FieldName": self.FieldName,
            "FieldType": self.FieldType,
            "FieldLabel": self.FieldLabel,
            "IsGroup": self.IsGroup,
            "GroupName": self.GroupName,
            "ValueMode": self.ValueMode,
            "IsRepeatable": self.IsRepeatable,
            "SelectSourceType": self.SelectSourceType,
            "SelectSourceValue": self.SelectSourceValue,
            "TableName": self.TableName,
            "ValueColumn": self.ValueColumn,
            "LabelColumn": self.LabelColumn,
            "StaticOptions": parse_static_options(self.StaticOptions) if self.StaticOptions else [],
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
        }
