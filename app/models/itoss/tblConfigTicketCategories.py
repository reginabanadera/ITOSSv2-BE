from database import db
from datetime import datetime
import pytz

philippines_tz = pytz.timezone('Asia/Manila')


class TicketCategory(db.Model):
    __tablename__ = 'tblConfigTicketCategories'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    Name = db.Column(db.String(70), nullable=False)
    ParentId = db.Column(db.Integer, nullable=True)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(50), nullable=True)
    DateModified = db.Column(db.String(50), nullable=True)
    ModifiedBy = db.Column(db.String(50), nullable=False)

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
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
            "ModifiedBy": self.ModifiedBy,
            "DateModified": self.DateModified
        }
