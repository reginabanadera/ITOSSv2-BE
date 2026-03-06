import os
from database import db
from dotenv import load_dotenv

class vwAtKWE(db.Model):
    load_dotenv()
    hris_db_name = os.getenv('HRIS_DB_NAME') 

    __tablename__ = 'vwAtKWE'
    __table_args__ = {'schema': f'{hris_db_name}.dbo'}
    __bind_key__ = 'hris_db'
    EmployeeId = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100))
    Department = db.Column(db.String(300))
    Section = db.Column(db.String(100))
    Area = db.Column(db.String(100))
    Designation = db.Column(db.String(300))
    DeptHeadId = db.Column(db.String(20))
    DateResigned = db.Column(db.String(100))
    Tag = db.Column(db.String(20))


    def to_dict(self):
        return {
            "EmployeeId": self.EmployeeId,
            "FullName": self.FullName,
            "Department": self.Department,
            "Section": self.Section,
            "Area": self.Area,
            "Designation": self.Designation,
            "DeptHeadId": self.DeptHeadId,
            "DateResigned": self.DateResigned,
            "Tag": self.Tag
        }