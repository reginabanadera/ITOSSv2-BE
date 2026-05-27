from database import db
from datetime import datetime
import pytz

philippines_tz = pytz.timezone('Asia/Manila')


class TicketApproverLevel(db.Model):
    __tablename__ = 'tblConfigTicketCategApprover'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    CategoryId = db.Column(
        db.Integer,
        db.ForeignKey('dbo.tblConfigTicketCategories.SystemId'),
        nullable=False
    )
    LevelNo = db.Column(db.Integer, nullable=False)
    ApproverType = db.Column(db.String(50), nullable=False)
    ApproverValue = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(50), nullable=True)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(50), nullable=True)

    

    def __init__ (self, CategoryId, LevelNo, ApproverType, ApproverValue, Description, CreatedBy, **kwargs):
        self.CategoryId = CategoryId
        self.LevelNo = LevelNo
        self.ApproverType = ApproverType
        self.ApproverValue = ApproverValue
        self.Description = Description
        self.CreatedBy = CreatedBy

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "CategoryId": self.CategoryId,
            "LevelNo": self.LevelNo,
            "ApproverType": self.ApproverType,
            "ApproverValue": self.ApproverValue,
            "Description": self.Description,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
        }
