import os
import markdown
import config
from auth_manager import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

def test_upload():
    creds = get_credentials()
    drive_service = build('drive', 'v3', credentials=creds)
    
    md_text = """# 멋진 보고서
## 1. 핵심 요약
- **정말** 대단한 내용입니다.
- 알아야 할 *모든 것*!

## 2. 상세 설명
마크다운이 아주 잘 적용됩니다.
"""
    html_text = markdown.markdown(md_text)
    
    # Wrap in basic HTML structure
    full_html = f"<html><body>{html_text}</body></html>"
    
    file_metadata = {
        'name': 'Test Markdown Doc',
        'mimeType': 'application/vnd.google-apps.document'
    }
    
    # Needs to be a file-like object
    media = MediaIoBaseUpload(io.BytesIO(full_html.encode('utf-8')), mimetype='text/html', resumable=True)
    
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print("Created Document ID:", file.get('id'))

if __name__ == "__main__":
    test_upload()
