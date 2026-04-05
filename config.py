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

# Gemini Model Selection
GEMINI_MODEL = "gemini-3-flash-preview"

# Default logic constants
DEFAULT_MIN_SUBSCRIBERS = 10000
DEFAULT_MIN_DURATION_MINS = 10
DEFAULT_MAX_DURATION_MINS = 60
DEFAULT_MAX_AGE_DAYS = 180

# AI Editor: number of past titles to consider for duplicate prevention
AI_EDITOR_PAST_TITLES_LIMIT = 20
# Maximum video IDs per YouTube API batch request
YOUTUBE_VIDEO_BATCH_LIMIT = 50
# AI Editor: top N candidates to evaluate
AI_EDITOR_TOP_CANDIDATES = 10
# YouTube search results per query
YOUTUBE_SEARCH_MAX_RESULTS = 20
# Number of AI-generated search queries
AI_SEARCH_QUERY_COUNT = 5

# NotebookLM polling
NLM_POLL_INTERVAL_SECS = 30
NLM_POLL_MAX_RETRIES = 60
