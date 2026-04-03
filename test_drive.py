import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import config

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

def test_drive():
    creds_path = config.GOOGLE_SERVICE_ACCOUNT_JSON
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {
        'name': 'Test Document via Drive API',
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    print("Testing Drive API File Creation...")
    try:
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"Success! File ID: {file.get('id')}")
    except Exception as e:
        print(f"Failed via Drive API: {e}")
        
    print("\nTesting Docs API...")
    docs_service = build('docs', 'v1', credentials=creds)
    try:
        doc = docs_service.documents().create(body={'title': 'Test Document via Docs API'}).execute()
        print(f"Success! Doc ID: {doc.get('documentId')}")
    except Exception as e:
        print(f"Failed via Docs API: {e}")

if __name__ == "__main__":
    test_drive()
