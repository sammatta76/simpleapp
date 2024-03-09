import fastapi
from fastapi.responses import RedirectResponse
import pandas as pd
from datetime import datetime, timedelta
from fastapi import HTTPException
import os
import gspread
from dotenv import load_dotenv
import re

# Load environment variables from the .env file
load_dotenv()


def get_df():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/"
    sheet_id = os.environ.get("ID2")
    df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
    return df


def get_employee_db(sheet_name):
    a = os.getenv("CREDENTIALS_PRIVATE_KEY").replace('\\n', "\n")
    credentials = {
        "type": os.getenv("CREDENTIALS_TYPE"),
        "project_id": os.getenv("CREDENTIALS_PROJECT_ID"),
        "private_key_id": os.getenv("CREDENTIALS_PRIVATE_KEY_ID"),
        "private_key": a,
        "client_email": os.getenv("CREDENTIALS_CLIENT_EMAIL"),
        "client_id": os.getenv("CREDENTIALS_CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER"),
        "client_x509_cert_url": os.getenv("CLIENT"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }
    gc = gspread.service_account_from_dict(credentials)
    sh = gc.open(sheet_name)
    wks = sh.worksheet("Sheet1")
    return wks


app = fastapi.FastAPI()

info = dict()


@app.get("/")
async def read_root():
    return {"message": "Ahla bi Nakhle"}


@app.get("/fetch-url/{name}/{id}/")
def id_func(name: str, id: "str"):
    try:
        a = get_info_by_name(name)
        database = a['database']
        update_swipes(id, database)
    except:
        print("Something went wrong")
    print("made it ")
    return fetch_url(name)


def update_swipes(id, sheet_name):
    wks = get_employee_db(sheet_name)
    cell_text = str(wks.find(id))
    matches = re.findall(r'R(\d+)C(\d+)', cell_text)

    if matches:
        R, C = map(int, matches[0])  # Convert matched strings to integers
        print("R:", R)
        print("C:", C)
        C += 1
        nswipes = wks.cell(R, C).value
        if nswipes == None:
            nswipes = 0
        wks.update_cell(R, C, int(nswipes) + 1)

    else:
        print("No 'R' and 'C' found in the cell text.")


@app.get("/fetch-url/{name}/")
def fetch_url(name: str):
    answer = validate(name)
    print(answer, "hello")
    if not answer:
        return {"message": "did not find name in database"}
    if answer == "nowebsite":
        return {"message": "subscription expired"}
    # url_path = info.get(name, "Hello")
    # google_url = "https://www.google.com"
    print("redirected")
    return RedirectResponse(url=answer)
    # return {"message": f"Fetching data from URL: {url_path}"}


# Function to get information by name from the Google Spreadsheet
def get_info_by_name(name):
    df = get_df()
    print("here")
    name = name.lower()
    result_df = df[df['name'] == name]
    if not result_df.empty:
        matching_row = result_df.iloc[0]
        website = matching_row['website']
        subscription_date = matching_row['subscription']
        database = matching_row['database']
        return {'name': name, 'website': website, 'subscription': subscription_date, 'database': database}
    else:
        return None


def is_within_40_days(date_str):
    try:
        # Convert string to datetime objects
        date_format = "%m/%d/%Y"
        input_date = datetime.strptime(date_str, date_format)

        # Get the current date
        current_date = datetime.now()

        # Calculate the difference in days
        date_difference = (current_date - input_date).days

        # Check if the difference is within 40 days
        return abs(date_difference) <= 40
    except ValueError:
        # Invalid date format
        raise HTTPException(status_code=400, detail="Invalid date format. Please use the format 'mm/dd/yyyy'.")


def validate(name):
    name = name.lower()
    info = get_info_by_name(name)
    if not info:
        print(f"{name} was not found")
        return False

    subscription_date = info['subscription']
    valid = is_within_40_days(subscription_date)

    # Check if it has been more than a month and 10 days
    if not valid:
        print(f"{name} Subscription has been active for more than a month and 10 days.")
        return "nowebsite"
    else:
        print(f"{name} Subscription is still within the allowed time.")
        return info["website"]
