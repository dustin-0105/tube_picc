import os
from googleapiclient.discovery import build
import config
from auth_manager import get_credentials
from datetime import datetime

def get_sheets_service():
    """Authenticates and returns the Sheets service client."""
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)

def get_active_topics():
    """
    Reads the 'Topics' sheet and returns a list of dictionaries for active topics.
    Headers expected: topic_id, topic_name, content_target, max_age_days, is_active
    """
    sheets_service = get_sheets_service()
    sheet_id = config.GOOGLE_SHEETS_ID
    
    if not sheet_id:
        raise ValueError("GOOGLE_SHEETS_ID is not configured in .env")
        
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='Topics!A:E'
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 2:
        return []
        
    headers = values[0]
    topics = []
    
    for row in values[1:]:
        # Ensure row has all elements
        while len(row) < len(headers):
            row.append("")
            
        topic = dict(zip(headers, row))
        
        # Check if is_active is TRUE 
        if str(topic.get('is_active', '')).upper() == 'TRUE':
            # Pre-process max_age_days to integer
            try:
                topic['max_age_days'] = int(topic.get('max_age_days', config.DEFAULT_MAX_DURATION_MINS))
            except ValueError:
                topic['max_age_days'] = 180
                
            topics.append(topic)
            
    return topics

def get_curated_video_ids():
    """
    Returns a set of all video_ids that have been previously curated to avoid duplicates.
    Expects 'History' sheet to have 'video_id' in column C.
    """
    sheets_service = get_sheets_service()
    sheet_id = config.GOOGLE_SHEETS_ID
    
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='History!A:F'
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 2:
        return set()
        
    headers = values[0]
    video_id_idx = -1
    
    # Dynamically find the video_id column index
    for i, header in enumerate(headers):
        if header.strip().lower() == 'video_id':
            video_id_idx = i
            break
            
    if video_id_idx == -1:
        # Fallback to index 2 (Column C) based on our spec
        video_id_idx = 2
        
    curated_ids = set()
    for row in values[1:]:
        if len(row) > video_id_idx and row[video_id_idx]:
            curated_ids.add(row[video_id_idx].strip())
            
    return curated_ids

def get_curated_history_for_topic(topic_id):
    """
    Returns a list of titles previously curated for the specific topic_id.
    This helps the AI Curation Director understand what angles were covered before.
    Expects 'History' sheet to have 'topic_id' in col A (index 0) and 'title' in col D (index 3).
    """
    sheets_service = get_sheets_service()
    sheet_id = config.GOOGLE_SHEETS_ID
    
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range='History!A:F'
    ).execute()
    
    values = result.get('values', [])
    if not values or len(values) < 2:
        return []
        
    headers = values[0]
    
    # Try finding exact columns dynamically
    topic_id_idx = next((i for i, h in enumerate(headers) if h.strip().lower() == 'topic_id'), 0)
    title_idx = next((i for i, h in enumerate(headers) if h.strip().lower() == 'title'), 3)
    
    past_titles = []
    
    for row in values[1:]:
        # Ensure row has enough columns
        if len(row) > max(topic_id_idx, title_idx):
            if row[topic_id_idx].strip() == str(topic_id):
                past_titles.append(row[title_idx].strip())
                
    return past_titles

def log_video_to_history(topic_id, topic_name, video_id, title, doc_url):
    """
    Appends the successfully curated video to the History sheet.
    Headers: topic_id, topic_name, video_id, title, date_posted, doc_url
    """
    sheets_service = get_sheets_service()
    sheet_id = config.GOOGLE_SHEETS_ID
    
    date_posted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    row_data = [
        str(topic_id),
        str(topic_name),
        str(video_id),
        str(title),
        date_posted,
        str(doc_url)
    ]
    
    body = {
        'values': [row_data]
    }
    
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range='History!A:F',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
    
if __name__ == "__main__":
    print("Testing get_active_topics()...")
    topics = get_active_topics()
    for t in topics:
        print(t)
