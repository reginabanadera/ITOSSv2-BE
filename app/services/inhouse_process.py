import os
from database import db
from flask import current_app, g
from sqlalchemy import text
from app.models.itoss.tblConfigSystemProfile import SystemProfile
from app.models.hris.vwAtKWE import vwAtKWE
from app.services.jwt_validator import token_required
from datetime import datetime
import pytz
import traceback

# Philippine timezone
ph_tz = pytz.timezone("Asia/Manila")

# Current PH time
now_ph = datetime.now(ph_tz)

formatted_datentime = now_ph.strftime("%Y-%m-%d %H:%M:%S")

@token_required
def process_access(system_key, userId, emailAddress, OASId, modules, fields_value):
    try:
        bind_map = current_app.config["SYSTEM_BIND_MAP"]

        current_username = g.payload['username']
        # Get system table config
        system = SystemProfile.query.filter(SystemProfile.SystemAlias == system_key).first()
        if system:
            tableName = system.DBTableName
            user_col = system.DBTableIdentifier
            bind = bind_map.get(system_key)
            engine = db.get_engine(current_app, bind=bind)


            # Get user info
            user = vwAtKWE.query.filter(vwAtKWE.EmployeeId == userId).first()
            if user:
                FullName = user.FullName

            #if type is MSSQL
            if system.DBType == "MSSQL":
                query = f"""
                    SELECT *
                    FROM {tableName}
                    WHERE OASId = :user_id
                """

                with engine.connect() as conn:
                    result = conn.execute(text(query), {"user_id": OASId}).fetchone()
                    if result:
                        module_data = {
                            module["ModuleName"]: 1
                            for module in modules
                        }

                        update_data = { **module_data, "user_id": OASId }

                        set_clause = ", ".join(
                            [f"[{col}] = :{col}" for col in module_data.keys()]
                        )

                        query = text(f"""
                            UPDATE {tableName}
                            SET {set_clause}
                            WHERE OASId = :user_id
                        """)

                        with engine.begin() as conn:
                            conn.execute(query, update_data)

                        return {
                            "success": True,
                            "action": "update",
                            "message": f"{system_key} account updated successfully."
                        }
                    else:
                        
                        #---------------------------------------I-LOG--------------------------------------------#
                        if system_key == "I-LOG":
                            ilog_name = user.CompleteName.title()
                            if user.Company == 'KWE Philippines':
                                company = "KINTETSU WORLD EXPRESS (PHILIPPINES) INC."
                            else:
                                company = user.Company

                            areadept = f"{user.Area} - {user.Department}"
                            userGroup = "User"

                            insert_data = {
                                "EmailAddress": emailAddress,
                                "EmployeeId": userId,
                                "FullName": ilog_name,
                                "Designation": user.Designation,
                                "Company": company, 
                                "Area": user.Area,
                                "Department": user.Department,
                                "AreaDepartment": areadept, 
                                "UserGroup": userGroup,
                                "Status": 1,
                                "CreatedBy": current_username,
                                "CreatedDate": formatted_datentime,
                                "OASId": OASId,
                                **modules
                            }

                        #----------------------------------------LOGMI----------------------------------------------#
                        elif system_key == "LOGMI":
                            logmi_name = user.CompleteName.title()
                            if user.Company == 'KWE Philippines':
                                company = "Kintetsu World Express (Philippines) Inc."
                            else:
                                company = user.Company

                            userGroup = "User"

                            module_data = {
                                module["ModuleName"]: 1
                                for module in modules
                            }

                            groups = [
                                "whse",
                                "rep",
                                "transct",
                                "trans",
                                "pod",
                                "misc",
                                "config",
                            ]

                            for group in groups:
                                if any(module["ModuleName"].lower().startswith(group) for module in modules):
                                    module_data[group] = 1

                            insert_data = {
                                "EmailAddress": emailAddress,
                                "FullName": logmi_name,
                                "Company": company, 
                                "Designation": user.Designation,
                                "UserGroup": userGroup,
                                "Status": 1,
                                "CreatedBy": current_username,
                                "CreatedDate": formatted_datentime,
                                "OASId": OASId,
                                **module_data
                            }

                        #------------------------------------------AccSys------------------------------------------------#
                        elif system_key == "AccSys":
                            accsys_name = user.CompleteName
                            company = user.Company
                            area = user.Area.title()

                            if "UserLevel" in fields_value:
                                userLevel = fields_value["UserLevel"]
                            else:
                                userLevel = None

                            if "UserAllowedCA" in fields_value:
                                allowedCA = fields_value["UserAllowedCA"]
                            else:
                                allowedCA = None

                            userGroup = "User"

                            insert_data = {
                                "EmailAddress": emailAddress,
                                "FullName": accsys_name,
                                "Designation": user.Designation,
                                "UserLevel": userLevel,
                                "Company": company, 
                                "Department": user.Department,
                                "ImmediateSuperior": user.ImmediateSupervisor,
                                "DepartmentHead": user.DepartmentHead,
                                "Area": area,
                                "UserGroup": userGroup,
                                "AllowedCAAmount": allowedCA,
                                "Status": 1,
                                "CreatedBy": current_username,
                                "CreatedDate": formatted_datentime,
                                "OASId": OASId,
                                **modules
                            }

                        #---------------------------------------------TIPISIMS------------------------------------------------------#
                        elif system_key == "TIPISIMS":
                            sims_name = user.CompleteName.title()
                            
                            if user.Company == 'KWE Philippines':
                                company = "Kintetsu World Express (Philippines) Inc."
                            else:
                                company = user.Company


                            if "XId" in fields_value:
                                xId = fields_value["XId"]
                            else:
                                xId = None

                            if "Department" in fields_value:
                                dept = fields_value["Department"]
                            else:
                                dept = user.Department

                            userGroup = "User"

                            insert_data = {
                                "EmployeeId": userId,
                                "XId": xId,
                                "Username": xId,
                                "FullName": sims_name,
                                "Designation": user.Designation,
                                "Company": company, 
                                "Department": dept,
                                "UserGroup": userGroup,
                                "Active": 1,
                                "CreatedBy": current_username,
                                "OASId": OASId,
                                **modules
                            }

                        #---------------------------------------------EAS-------------------------------------------------#
                        elif system_key == "EAS":
                            eas_name = user.CompleteName.title()
                            userGroup = "Administrator"

                            insert_data = {
                                "Email_Address": emailAddress,
                                "Full_Name": eas_name,
                                "Designation": user.Designation,
                                "UserGroup": userGroup,
                                "Active": 1,
                                "CreatedBy": current_username,
                                "CreatedDate": formatted_datentime,
                                "OASId": OASId,
                            }

                        #---------------------------------------------BILLSYS-----------------------------------------------------#
                        elif system_key == "BillSys":
                            billsys_name = user.CompleteName
                            company = user.Company
                            area = user.Area.title()

                            userGroup = "User"
                            stat = "Active"

                            insert_data = {
                                "EmailAddress": emailAddress,
                                "FullName": billsys_name,
                                "Designation": user.Designation,
                                "Company": company, 
                                "Department": user.Department,
                                "Area": area,
                                "UserGroup": userGroup,
                                "Status": stat,
                                "CreatedBy": current_username,
                                "CreatedDate": formatted_datentime,
                                "OASId": OASId,
                                **modules
                            }

                        columns = ", ".join(f"[{c}]" for c in insert_data.keys())
                        values = ", ".join(f":{c}" for c in insert_data.keys())

                        query = text(f"""
                            INSERT INTO {tableName}
                            ({columns})
                            VALUES ({values})
                        """)

                        with engine.begin() as conn:
                            conn.execute(query, insert_data)

                        return {
                            "success": True,
                            "action": "insert",
                            "message": f"{system_key} account inserted successfully."
                        }
    except Exception as ex:
        print("=== ERROR PROCESSING TICKET ===")
        traceback.print_exc()
        return {
            "success": False,
            "message": str(ex),
            "traceback": traceback.format_exc()
        }

        
    
