import os
from database import db
from dotenv import load_dotenv

class vwImmediateSuperior(db.Model):
    load_dotenv()
    hris_db_name = os.getenv('HRIS_DB_NAME') 

    __tablename__ = 'vwImmediateSuperior'
    __table_args__ = {'schema': f'{hris_db_name}.dbo'}
    __bind_key__ = 'hris_db'
    EmployeeId = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100))
    Department = db.Column(db.String(300))
    Tag = db.Column(db.String(20))


    def to_dict(self):
        return {
            "EmployeeId": self.EmployeeId,
            "Name": self.Name,
            "Department": self.Department,
            "Tag": self.Tag
        }