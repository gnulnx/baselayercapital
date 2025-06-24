import gspread
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_file(
    "secrets/google-sheets-creds.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
)
client = gspread.authorize(creds)

# Replace with your actual spreadsheet key
sheet = client.open_by_key("121IKOMNzhxJfcci-QifPw6p3aYabzalMH6w2iB8ueAU")
worksheet = sheet.worksheet("Accounts Overview")
# Just get all values
raw_data = worksheet.get_all_values()

# Debug/inspect:
for row in raw_data:
    print(row)
