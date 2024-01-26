import fastapi
from fastapi.responses import RedirectResponse
# from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
from fastapi import HTTPException
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

#




def get_df():
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/"
    sheet_id = os.environ.get("SHEET_ID")
    df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")
    return df



# df = pd.read_excel(excel_file_path)



app = fastapi.FastAPI()

info = dict()


@app.get("/")
async def read_root():
    return {"message": "Ahla bi Nakhle"}



@app.get("/fetch-url/{name}/")
async def fetch_url(name: str):
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



# def get_info_by_name(name):
#     print("here")
#     name = name.lower()
#     result_df = df[df['name'] == name]
#     if not result_df.empty:
#         matching_row = result_df.iloc[0]
#         website = matching_row['website']
#         subscription_date = matching_row['subscription']
#         formatted_date = pd.to_datetime(subscription_date.strftime('%m-%d-%Y'))
#         return {'name': name, 'website': website, 'subscription': formatted_date}
#     else:
#         return None


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
        return {'name': name, 'website': website, 'subscription': subscription_date}
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
