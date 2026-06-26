from database import db
from datetime import datetime
import pytz
import json

philippines_tz = pytz.timezone('Asia/Manila')

class TicketAssignment(db.Model):
    __tablename__ = 'tblConfigTicketAssignment'
    __table_args__ = {'schema': 'dbo'}

    SystemId = db.Column(db.Integer, primary_key=True, nullable=False)
    CategoryId = db.Column(
        db.Integer,
        db.ForeignKey('dbo.tblConfigTicketCategories.SystemId'),
        nullable=False
    )
    GroupName = db.Column(db.String(50), nullable=False)
    Member = db.Column(db.String(50), nullable=False)
    MemberEmail = db.Column(db.String(90), nullable=True)
    DateCreated = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    CreatedBy = db.Column(db.String(90), nullable=True)


    def __init__ (self, CategoryId, GroupName, Member, MemberEmail, CreatedBy, **kwargs):
        self.CategoryId = CategoryId
        self.GroupName = GroupName
        self.Member = Member
        self.MemberEmail = MemberEmail
        self.CreatedBy = CreatedBy

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "CategoryId": self.CategoryId,
            "Member": self.Member,
            "MemberEmail": self.MemberEmail,
            "DateCreated": self.DateCreated.isoformat() if self.DateCreated else None,
            "CreatedBy": self.CreatedBy,
        }


    