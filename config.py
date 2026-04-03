import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Configs
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
GOOGLE_OAUTH_CREDENTIALS = os.getenv("GOOGLE_OAUTH_CREDENTIALS", "credentials.json")
GOOGLE_OAUTH_TOKEN = os.getenv("GOOGLE_OAUTH_TOKEN", "token.json")
GOOGLE_DRIVE_DOCS_FOLDER_ID = os.getenv("GOOGLE_DRIVE_DOCS_FOLDER_ID")
GOOGLE_DRIVE_AUDIO_FOLDER_ID = os.getenv("GOOGLE_DRIVE_AUDIO_FOLDER_ID")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")

# OAuth Scopes required for all Google services
GOOGLE_OAUTH_SCOPES = [
    'https://www.googleapis.com/auth/documents', 
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

# Gemini Model Selection (Defaults to gemini-2.5-flash)
GEMINI_MODEL = "gemini-2.5-flash"

# Default logic constants
DEFAULT_MIN_SUBSCRIBERS = 10000
DEFAULT_MIN_DURATION_MINS = 10
DEFAULT_MAX_DURATION_MINS = 60
