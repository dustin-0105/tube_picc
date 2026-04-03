import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import config

def get_transcript(video_id, fallback_text=""):
    """
    Attempts to fetch the YouTube video transcript (including auto-generated).
    Falls back to `fallback_text` if transcripts are disabled or unavailable.
    """
    try:
        # Fetch available transcripts directly
        # Preference: ko -> en
        transcript_list = YouTubeTranscriptApi().list(video_id)
        transcript = transcript_list.find_transcript(['ko', 'en'])
        trans_data = transcript.fetch()
        
        formatter = TextFormatter()
        text_content = formatter.format_transcript(trans_data)
        
        if not text_content.strip():
            raise ValueError("Transcript is empty.")
            
        return text_content
        
    except Exception as e:
        print(f"⚠️ Could not fetch transcript for {video_id}: {e}")
        print("💡 Falling back to title and description.")
        return fallback_text

def summarize_video(video_data, prompt_text):
    """
    Summarizes the video text using Gemini API.
    video_data: dict containing title, description, url, video_id
    prompt_text: the system prompt text to guide Gemini
    """
    genai.configure(api_key=config.GEMINI_API_KEY)
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")
    
    # Initialize the specific model defined in configuration
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    # 1. Fetch transcript or construct a fallback context string
    fallback_metadata = f"Title: {video_data.get('title', 'Unknown')}\nDescription: {video_data.get('description', 'Unknown')}"
    video_text = get_transcript(video_data['video_id'], fallback_text=fallback_metadata)
    
    # 2. Combine system prompt with the video content
    full_prompt = f"{prompt_text}\n\n[영상 메타데이터]\n{fallback_metadata}\n\n[영상 스크립트/내용]\n{video_text}"
    
    # 3. Request generation from Gemini
    # Adding a generation config could be helpful to control temperature if needed.
    response = model.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.7, # Balanced for summary creation
        )
    )
    
    if not response.text:
       raise ValueError("Gemini returned an empty response. The content may have been blocked or the video text was insufficient.")
       
    return response.text

if __name__ == "__main__":
    # ---------------------------------------------------------
    # INDEPENDENT TEST BLOCK
    # ---------------------------------------------------------
    print("Testing summarizer.py...")
    try:
        # Load the default phase 1 prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "summarize.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            test_prompt = f.read()
            
        # Dummy video data (Me at the zoo - very short video)
        test_video = {
            "video_id": "jNQXAC9IVRw",
            "title": "Me at the zoo",
            "description": "The first video on YouTube."
        }
        
        print(f"\nRunning Gemini Summarization on '{test_video['title']}'...")
        result = summarize_video(test_video, test_prompt)
        
        print("\n✅ [GEMINI OUTPUT]")
        print("--------------------------------------------------")
        print(result)
        print("--------------------------------------------------")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Ensure that your GEMINI_API_KEY is correctly set in the .env file!")
