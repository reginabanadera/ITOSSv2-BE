from openpyxl import load_workbook
import uuid
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

output_dir = os.path.join(BASE_DIR, "..", "generated")
output_dir = os.path.normpath(output_dir)

os.makedirs(output_dir, exist_ok=True)

def fill_excel_template(template_name, template_path, fields):

    wb = load_workbook(template_path)
    ws = wb.active

    if template_name == "UFSCreation":
        fill_ufs_creation(ws, fields)


    elif template_name == "URSCreation":
        fill_urs_creation(ws, fields)

    filename = f"{uuid.uuid4()}.xlsx"
    output_path = os.path.join(output_dir, filename)

    wb.save(output_path)

    return output_path

def fill_ufs_creation(ws, fields):
    first_name = fields.get("FirstName", "")
    last_name = fields.get("LastName", "")
    emailaddress = fields.get("EmailAddress", "")
    terminals = fields.get("Terminal", [])

    start_row = 12

    for index, terminal in enumerate(terminals):
        row = start_row + index

        ws[f"B{row}"] = terminal.get("RequestType", "")
        ws[f"E{row}"] = first_name
        ws[f"F{row}"] = last_name
        ws[f"G{row}"] = terminal.get("TerminalId", "")
        ws[f"J{row}"] = emailaddress
        ws[f"L{row}"] = terminal.get("SecurityLevel", "")
        ws[f"P{row}"] = terminal.get("HighSecurityUser", "")

def fill_urs_creation(ws, fields):
    first_name = fields.get("FirstName", "")
    last_name = fields.get("LastName", "")
    terminals = fields.get("Terminal", [])

    start_row = 14

    for index, terminal in enumerate(terminals):
        row = start_row + index

        ws[f"B{row}"] = terminal.get("RequestType", "")
        ws[f"E{row}"] = first_name
        ws[f"F{row}"] = last_name
        ws[f"G{row}"] = terminal.get("TerminalId", "")
        ws[f"H{row}"] = terminal.get("Authority", "")
        ws[f"I{row}"] = terminal.get("LoginModeUFSAE", "")
        ws[f"J{row}"] = terminal.get("LoginModeUFSAI", "")
        ws[f"K{row}"] = terminal.get("LoginModeUFSOE", "")
        ws[f"L{row}"] = terminal.get("LoginModeUFSOI", "")
        ws[f"M{row}"] = terminal.get("LoginModeUAS", "")
        ws[f"N{row}"] = terminal.get("LoginModeProfile", "")
        ws[f"O{row}"] = terminal.get("SecurityLevel", "")
        ws[f"P{row}"] = "570"

       