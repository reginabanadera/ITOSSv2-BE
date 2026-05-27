from database import db
from datetime import datetime
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


class TicketCategory(db.Model):
    __tablename__ = 'tblConfigTicketCategories'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    Name = db.Column(db.String(70), nullable=False)
    ParentId = db.Column(db.Integer, nullable=True)
    Inhouse = db.Column(
        db.Integer,
        db.ForeignKey('tblConfigSystemProfile.SystemAlias'),
        nullable=True
    )
    Description = db.Column(db.String(500), nullable=True)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(50), nullable=True)
    DateModified = db.Column(db.String(50), nullable=True)
    ModifiedBy = db.Column(db.String(50), nullable=False)

    approvers = db.relationship(
        "TicketApproverLevel",
        backref="category",
        lazy=True
    )

    custom_fields = db.relationship(
        "TicketCustomFields",
        backref="category",
        lazy=True
    )

    def __init__ (self, Name, CreatedBy, **kwargs):
        self.Name = Name
        self.CreatedBy = CreatedBy

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "Name": self.Name,
            "ParentId": self.ParentId,
            "Inhouse": self.Inhouse,
            "Description": self.Description,
            "approvers": [
                {   
                    "LevelNo": a.LevelNo,
                    "ApproverType": a.ApproverType,
                    "ApproverValue": a.ApproverValue,
                    "Description": a.Description
                }
                for a in self.approvers
            ],
            "custom_fields" : [
                {
                    "FieldName": c.FieldName,
                    "FieldType": c.FieldType,
                    "FieldLabel": c.FieldLabel,
                    "IsGroup": c.IsGroup,
                    "GroupName": c.GroupName,
                    "ValueMode": c.ValueMode,
                    "IsRepeatable": c.IsRepeatable,
                    "SelectSourceType": c.SelectSourceType,
                    "SelectSourceValue": c.SelectSourceValue,
                    "TableName": c.TableName,
                    "ValueColumn": c.ValueColumn,
                    "LabelColumn": c.LabelColumn,
                    "StaticOptions": parse_static_options(c.StaticOptions) if c.StaticOptions else [],
                }
                for c in self.custom_fields
            ],
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
            "ModifiedBy": self.ModifiedBy,
            "DateModified": self.DateModified
        }
