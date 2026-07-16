from app.models.kweph_mfa.tblConsolidated import Users_MFA
from app.models.hris.vwAtKWE import vwAtKWE
from database import db
from app.services.encryption_services import hash_password
from datetime import datetime

def check_mfa(id, email):
    try:
        check = Users_MFA.query.filter(Users_MFA.EmployeeId == id).first()
        if not check:
            hris = vwAtKWE.query.filter(vwAtKWE.EmployeeId == id).first()
            if hris:
                rawId = id[1:]
                dateHired = datetime.strptime(hris.DateHired, "%m/%d/%Y")
                setPass = f"KWE{id}"
                hash_pass = hash_password(setPass)

                if email:
                    emailAddress = email
                else:
                    emailAddress = hris.EmailAddress

                if hris.Company == "KWE Philippines" or hris.Company == "KINTETSU WORLD EXPRESS (PHILIPPINES) INC":
                    OASId = f"X01{dateHired.strftime('%Y%m%d')}{rawId}"
                else:
                    OASId = f"X02{dateHired.strftime('%Y%m%d')}{rawId}"

                new_mfa = Users_MFA(
                    OASId=OASId,
                    EmployeeId=id,
                    EmployeeName=hris.FullName,
                    EmailAddress=emailAddress,
                    Password=hash_pass,
                    Status=1,
                )
                db.session.add(new_mfa)
                db.session.commit()
        else:
            OASId = check.OASId
            
        return OASId


    except Exception as e:
        import traceback
        print("=== ERROR CHECKING MFA ===")
        traceback.print_exc()
