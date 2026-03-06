from database import db
from datetime import datetime, timedelta
import pytz

philippines_tz = pytz.timezone('Asia/Manila')


class DBColumns(db.Model):
    __tablename__ = "tblConfigDBColumns"
    SystemId = db.Column(db.Integer, primary_key=True)
    SystemAlias = db.Column(db.String(50), nullable=False)
    DBColumn = db.Column(db.String(150), nullable=True)
    Description = db.Column(db.String(200), nullable=True)
    ColGroup = db.Column(db.String(50), nullable=False)
    Status = db.Column(db.String(10), nullable=False)
    DateImported = db.Column(db.DateTime, default=lambda: datetime.now(philippines_tz))
    ImportedBy = db.Column(db.String(150), nullable=False)
    ModifiedBy = db.Column(db.String(150), nullable=True)
    DateModified = db.Column(db.String(70), nullable=True)

    def __init__ (self, SystemAlias, DBColumn, ImportedBy, Status):
        self.SystemAlias = SystemAlias
        self.DBColumn = DBColumn
        self.ImportedBy = ImportedBy
        self.Status = Status

    
    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "SystemAlias": self.SystemAlias,
            "DBColumn": self.DBColumn,
            "Description": self.Description,
            "ColGroup": self.ColGroup,
            "Status": self.Status,
            "DateImported": self.DateImported,
            "ModifiedBy": self.ModifiedBy,
            "DateModified": self.DateModified,
        }