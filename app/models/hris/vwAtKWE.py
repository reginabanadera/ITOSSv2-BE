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
    CompleteName = db.Column(db.String(100))
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    EmailAddress = db.Column(db.String(80)) #should depend on ITOSS EmailAddress
    Company = db.Column(db.String(150))
    Designation = db.Column(db.String(300))
    Department = db.Column(db.String(300))
    Section = db.Column(db.String(100))
    Area = db.Column(db.String(100))
    DateResigned = db.Column(db.String(100))
    DepartmentHead = db.Column(db.String(100))
    ImmediateSupervisor = db.Column(db.String(100))
    SuperiorId = db.Column(db.String(15))
    DeptHeadId = db.Column(db.String(15))
    DeptHeadEmailAdd = db.Column(db.String(100))
    ISEmailAdd = db.Column(db.String(100))
    EmpLevel = db.Column(db.String(20))
    Tag = db.Column(db.String(20))
    DateHired = db.Column(db.String(50))

    def to_dict(self):
        return {
            "EmployeeId": self.EmployeeId,
            "FullName": self.FullName,
            "CompleteName": self.CompleteName,
            "FirstName": self.FirstName,
            "LastName": self.LastName,
            "EmailAddress": self.EmailAddress,
            "Designation": self.Designation,
            "Company": self.Company,
            "Department": self.Department,
            "Section": self.Section,
            "Area": self.Area,
            "DateResigned": self.DateResigned,
            "DepartmentHead": self.DepartmentHead,
            "ImmediateSupervisor": self.ImmediateSupervisor,
            "SuperiorId": self.SuperiorId,
            "DeptHeadId": self.DeptHeadId,
            "DeptHeadEmailAdd": self.DeptHeadEmailAdd,
            "ISEmailAdd": self.ISEmailAdd,
            "EmpLevel": self.EmpLevel,
            "Tag": self.Tag,
            "DateHired": self.DateHired
        }