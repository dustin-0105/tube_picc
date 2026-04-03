import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import config
from auth_manager import get_credentials

def get_drive_service():
    """Authenticates and returns the Drive service client."""
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

def upload_file_to_drive(file_path, file_name, folder_id, mime_type='audio/wav'):
    """
    Uploads a local file to a specific Google Drive folder and makes it publicly accessible.
    
    Args:
        file_path (str): The local path to the file.
        file_name (str): The logical name to give the file in Google Drive.
        folder_id (str): The ID of the Drive folder where it should be stored.
        mime_type (str): The MIME type of the file.
        
    Returns:
        str: The public view URL of the uploaded file.
    """
    drive_service = get_drive_service()
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id] if folder_id else []
    }
    
    media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
    
    print(f"Uploading {file_name} to Google Drive...")
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    file_id = file.get('id')
    
    # Make it publicly readable
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    drive_service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id',
    ).execute()
    
    # Shareable link
    public_url = f"https://drive.google.com/file/d/{file_id}/view"
    return public_url
