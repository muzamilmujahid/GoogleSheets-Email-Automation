import os
import pandas as pd
from send_email import send_email
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build # creates sheets API client
from google.oauth2.service_account import Credentials # loads OAuth token

# load sheet details
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
load_dotenv(current_dir / ".env")

SERVICE_ACCOUNT = "sheet_credentials.json"
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")
SHEET_RANGE = f"{SHEET_NAME}!A:D" # read first four columns of sheet

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"] # read and edit sheet

def load_df():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT, scopes = SCOPES)

    service = build("sheets", "v4", credentials=creds) # making Sheets API client
    resp = service.spreadsheets().values().get( # reading values within specified range
        spreadsheetId = SHEET_ID,
        range = SHEET_RANGE
    ).execute()

    values = resp.get("values", []) # extract data as rows
   
    if not values: # return empty frame if there are no values in the sheet
        return pd.DataFrame(), service, []

    headers = values[0] # first row is headers
    rows = values [1:] # rest of rows are data

    df = pd.DataFrame(rows, columns = headers) # setting rows and columns
    return df, service, headers

def update_email_status(service, sheet_row_number, email_col_number):
    sheet_col_letter = chr(ord("A") + email_col_number) # making sheet column letter into numbers (A=0, B=1, ...)
    target_range = f"{SHEET_NAME}!{sheet_col_letter}{sheet_row_number}"

    service.spreadsheets().values().update( # updating the sheet after email is sent
        spreadsheetId = SHEET_ID,
        range = target_range,
        valueInputOption = "RAW",
        body = {"values": [["Y"]]}
    ).execute()

def query_data_and_send_emails(df, service, headers):
    email_counter = 0
    sheet_email_sent_col = headers.index("Email Sent") # finding column/header of email sent status

    for i, row in df.iterrows(): # going through all rows (startups)
        sheet_row_number = i + 2
        if pd.isna(row["Email Sent"]) or str(row["Email Sent"]).strip() == "": # sending email if the Email Sent cell is empty
            send_email(
                receiver_email = row["Email"],
                name = row["Founder Name"]
            )
            update_email_status(service, sheet_row_number, sheet_email_sent_col) # update email status on sheet
            email_counter += 1
    return f"Total Emails Sent = {email_counter}" # return total number of email sent

# Main use
df, service, headers = load_df()
result = query_data_and_send_emails(df, service, headers)
print(result)