from database import db

class Users(db.Model):
    __tablename__ = 'tblUsers'
    SystemId = db.Column(db.Integer, primary_key=True)
    OASId = db.Column(db.String(20), nullable=False)
    EmployeeId = db.Column(db.String(20), nullable=True)
    EmployeeName = db.Column(db.String(150), nullable=False)
    Password = db.Column(db.String(70), nullable=False)
    EmailAddress = db.Column(db.String(170), nullable=True)
    Designation = db.Column(db.String(300), nullable=True)
    Department = db.Column(db.String(300), nullable=True)
    Section = db.Column(db.String(300), nullable=True)
    UserGroup = db.Column(db.String(50), nullable=True)
    Status = db.Column(db.String(1), nullable=False)
    CreatedBy = db.Column(db.String(170), nullable=True)

    def __init__ (self, OASId, EmployeeId, EmployeeName, EmailAddress, Designation, Department, Section, UserGroup, Status, CreatetedBy):
        self.OASId = OASId
        self.EmployeeId = EmployeeId
        self.EmployeeName = EmployeeName
        self.EmailAddress = EmailAddress
        self.Designation = Designation
        self.Department = Department
        self.Section = Section
        self.UserGroup = UserGroup
        self.Status = Status
        self.CreatedBy = CreatetedBy

    def to_dict(self):
        return {
            "SystemId": self.SystemId,
            "OASId": self.OASId,
            "EmployeeId": self.EmployeeId,
            "EmployeeName": self.EmployeeName,
            "EmailAddress": self.EmailAddress,
            "Designation": self.Designation,
            "Department": self.Department,
            "Section": self.Section,
            "UserGroup": self.UserGroup,
            "Status": self.Status,
            "CreatedBy": self.CreatedBy
        }
