import os
import io
import markdown
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import config
from auth_manager import get_credentials

def get_google_services():
    """Authenticates and returns the Docs and Drive service clients."""
    creds = get_credentials()
    # Build API clients
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    
    return docs_service, drive_service

def create_summary_doc(video_data, summary_text, topic_name, related_videos=None):
    """
    Creates a new Google Doc, formats it with the video metadata and Gemini summary,
    and makes it publicly accessible.
    
    Returns the URL of the created document.
    """
    docs_service, drive_service = get_google_services()
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    doc_title = f"[{today_str}] {video_data['title']} ({topic_name})"
    
    # 1. Create a blank document inside the specified Drive folder
    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [config.GOOGLE_DRIVE_DOCS_FOLDER_ID] if config.GOOGLE_DRIVE_DOCS_FOLDER_ID else []
    }
    
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    document_id = file.get('id')
    
    # 2. Build full Markdown content
    
    related_md = ""
    if related_videos:
        related_md = "\n## 💡 관련 추천 콘텐츠\n"
        for idx, r in enumerate(related_videos, start=1):
            related_md += f"{idx}. [{r['title']}]({r['url']}) — {r['channel_name']} ({r['duration_mins']}분)\n"
            
    content_md = (
        f"# {video_data['title']}\n\n"
        f"**채널:** {video_data['channel_name']}\n\n"
        f"**길이:** {video_data['duration_mins']}분\n\n"
        f"**유튜브 링크:** [{video_data['url']}]({video_data['url']})\n\n"
        f"**주제:** {topic_name}\n\n"
        f"**작성일:** {today_str}\n\n"
        f"---\n\n"
        f"{summary_text}\n"
        f"{related_md}\n"
        f"---\n"
        f"*이 문서는 YouTube Content Curation Bot에 의해 자동 생성되었습니다.*\n"
    )
    
    # 3. Convert Markdown to HTML
    html_text = markdown.markdown(content_md)
    # Wrap in basic HTML structure so Google Drive parses it nicely as a document
    full_html = f"<html><body>{html_text}</body></html>"
    
    # 4. Upload HTML content directly as a Google Doc via Drive API
    media = MediaIoBaseUpload(io.BytesIO(full_html.encode('utf-8')), mimetype='text/html', resumable=True)
    
    # Update the blank file with the html content
    drive_service.files().update(
        fileId=document_id,
        media_body=media
    ).execute()
        
    # 3. Share the document publicly (Anyone with link can view)
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    
    drive_service.permissions().create(
        fileId=document_id,
        body=permission,
        fields='id',
    ).execute()
    
    # Return a shareable edit/view link
    doc_url = f"https://docs.google.com/document/d/{document_id}/view"
    return doc_url

if __name__ == "__main__":
    # ---------------------------------------------------------
    # INDEPENDENT TEST BLOCK
    # ---------------------------------------------------------
    print("Testing docs_manager.py...")
    try:
        # Dummy video and text for testing Google credentials
        test_video = {
            "title": "구글 문서 API 테스트",
            "channel_name": "Test Channel",
            "duration_mins": 10,
            "url": "https://www.youtube.com/watch?v=test"
        }
        test_summary = "## 핵심 요약\n- 문서 생성이 원활히 작동하는지 확인합니다.\n- 권한이 '링크가 있는 모든 사용자'인지 확인합니다.\n\n## 상세 내용\n이곳에는 Gemini가 작성한 긴 텍스트가 삽입됩니다."
        test_topic = "Development Tests"
        
        test_related = [
            {
                "title": "관련 영상 테스트",
                "channel_name": "Test Channel 2",
                "duration_mins": 5,
                "url": "https://youtube.com/watch?v=related1"
            }
        ]
        
        print(f"Attempting to generate Google Doc for '{test_video['title']}'...")
        doc_url = create_summary_doc(test_video, test_summary, test_topic, test_related)
        
        print("\n✅ [DOCUMENT CREATED SUCCESSFULLY]")
        print("--------------------------------------------------")
        print(f"Public Link: {doc_url}")
        print("--------------------------------------------------")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 The service_account.json must be present in this folder, and have Docs & Drive API enabled.")
