import msal
import requests
import os

# 1. Configuration (Use your .env file for these!)
from dotenv import load_dotenv

load_dotenv()  # This looks for the .env file automatically


CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# 2. Get the Access Token
app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
token_response = app.acquire_token_for_client(scopes=SCOPE)
access_token = token_response.get('access_token')

# 3. Send the Email via Graph API
user_email = "conor@horatiopistachio.com"
endpoint = f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail"

email_data = {
    "message": {
        "subject": "Scraper Update",
        "body": {"contentType": "Text", "content": "The latest links are ready!"},
        "toRecipients": [{"emailAddress": {"address": "bigman@gmail.com"}}]
    }
}

response = requests.post(endpoint, json=email_data, headers={'Authorization': f'Bearer {access_token}'})
print(response)
if response.status_code == 202:
    print("Email sent via Graph API!")