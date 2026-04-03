import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import config

def get_credentials():
    """Authenticates the user and returns valid Google Credentials."""
    creds = None
    if os.path.exists(config.GOOGLE_OAUTH_TOKEN):
        creds = Credentials.from_authorized_user_file(
            config.GOOGLE_OAUTH_TOKEN, config.GOOGLE_OAUTH_SCOPES
        )
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GOOGLE_OAUTH_CREDENTIALS, config.GOOGLE_OAUTH_SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        with open(config.GOOGLE_OAUTH_TOKEN, "w") as token:
            token.write(creds.to_json())
            
    return creds
