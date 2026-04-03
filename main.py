import os
import config
from sheets_manager import get_active_topics, log_video_to_history, get_curated_history_for_topic
from youtube_search import search_educational_videos
from summarizer import summarize_video
from docs_manager import create_summary_doc
from slack_notifier import send_slack_message, send_daily_audio_message
from notebooklm_manager import create_daily_audio_overview
from drive_manager import upload_file_to_drive
from datetime import datetime

def main():
    print("🚀 Starting YouTube Content Curation Bot (Phase 5: Master Podcast)...\n")
    
    # 1. Fetch active topics from Google Sheets
    print("▶️ [STEP 1] Fetching Active Topics from Google Sheets...")
    topics = get_active_topics()
    
    if not topics:
        print("  ❌ No active topics found in the 'Topics' sheet. Exiting.")
        return
        
    print(f"  ✅ Found {len(topics)} active topic(s).")
    
    # Load the common summarization prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "summarize.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    # Collectors for Master Podcast Generation
    curated_doc_urls = []
    curated_youtube_urls = []
    pending_notifications = []

    # Loop through each topic
    for topic in topics:
        topic_id = topic.get("topic_id", "0")
        topic_name = topic.get("topic_name", "Unknown")
        content_target = topic.get("content_target", "")
        max_age = topic.get("max_age_days", 180)
        
        print(f"\n=======================================================")
        print(f"🎬 Processing Topic: [{topic_id}] {topic_name}")
        print(f"=======================================================")
        
        # Fetch past curated titles for AI Editor duplicate prevention
        past_titles = get_curated_history_for_topic(topic_id)
        if past_titles:
            print(f"  📚 Found {len(past_titles)} past videos for this topic.")
        else:
            print(f"  📚 No past videos found. Fresh start!")
            
        print(f"▶️ [STEP 2] Searching YouTube for '{topic_name}' target: {content_target[:30]}...")
        featured, related = search_educational_videos(topic_name, content_target, max_age_days=max_age, past_titles=past_titles)
        
        if not featured:
            print(f"  ⏭️ No optimal uncurated videos found for '{topic_name}'. Skipping.")
            continue
            
        print(f"  ✅ Selected Featured Video: '{featured['title']}' ({featured['channel_name']})")
        
        # Summarize Video with Gemini
        print(f"\n▶️ [STEP 3] Generating AI summary for '{featured['title']}'...")
        try:
            summary_text = summarize_video(featured, prompt_text)
            print("  ✅ Summary generated successfully!")
        except Exception as e:
            print(f"  ❌ Summarization failed: {e}. Skipping.")
            continue
        
        # Create Google Doc
        print("\n▶️ [STEP 4] Creating public Google Doc...")
        try:
            doc_url = create_summary_doc(featured, summary_text, topic_name, related)
            print(f"  ✅ Document URL: {doc_url}")
        except Exception as e:
            print(f"  ❌ Document creation failed: {e}. Skipping.")
            continue
        
        # Record for delayed Slack notifications
        pending_notifications.append({
            "topic_id": topic_id,
            "topic_name": topic_name,
            "featured": featured,
            "doc_url": doc_url,
            "summary_text": summary_text
        })
        
        # Log to History Sheet immediately so we don't curate this again tomorrow
        print("  📝 Logging video to History sheet...")
        try:
            log_video_to_history(
                topic_id=topic_id,
                topic_name=topic_name,
                video_id=featured['video_id'],
                title=featured['title'],
                doc_url=doc_url
            )
            print("  ✅ Logged successfully.")
        except Exception as e:
            print(f"  ⚠️ History log failed: {e}")
            
        # Success across all steps for this topic!
        curated_doc_urls.append(doc_url)
        curated_youtube_urls.append(featured['url'])
             
    print("\n🎉 ALL TOPIC CRAWLING COMPLETED SUCCESSFULLY!")
    
    # -------------------------------------------------------------
    # PHASE 5: Master Audio Podcast Generation
    # -------------------------------------------------------------
    if curated_doc_urls and curated_youtube_urls:
        print("\n▶️ [STEP 6] Generating Master AI Podcast overview for today's topics...")
        audio_file_path = create_daily_audio_overview(curated_doc_urls, curated_youtube_urls)
        
        if audio_file_path:
            today_str = datetime.now().strftime("%Y-%m-%d")
            audio_filename = f"[{today_str}] 큐레이션 통합 오디오 브리핑.wav"
            
            print(f"\n▶️ [STEP 7] Uploading Master AI Podcast '{audio_filename}' to Google Drive...")
            public_audio_url = upload_file_to_drive(
                file_path=audio_file_path, 
                file_name=audio_filename, 
                folder_id=config.GOOGLE_DRIVE_AUDIO_FOLDER_ID,
                mime_type='audio/wav'  # or audio/mpeg if it drops mp3
            )
            
            print(f"  ✅ Uploaded to Google Drive: {public_audio_url}")
            
            # Send Slack notification for Podcast
            print("\n▶️ [STEP 8] Sending Master Podcast Notification to Slack...")
            slack_audio_success = send_daily_audio_message(public_audio_url)
            if slack_audio_success:
                print("  ✅ Podcast Slack notification sent!")
            else:
                print("  ⚠️ Podcast Slack notification failed.")
        else:
            print("  ⚠️ Audio generation timed out or failed. Skipping Drive upload.")
            
    else:
        print("\nℹ️ No new curations today. Skipping Master Podcast generation.")
        
    # -------------------------------------------------------------
    # PHASE 6: Flush Delayed Slack Notifications
    # -------------------------------------------------------------
    if pending_notifications:
        print("\n▶️ [STEP 9] Sending Delayed Individual Slack Notifications...")
        for notif in pending_notifications:
            print(f"  > Notifying for '{notif['topic_name']}'...")
            send_slack_message(
                topic_name=notif['topic_name'], 
                featured_video=notif['featured'], 
                doc_url=notif['doc_url'], 
                summary_text=notif['summary_text']
            )
        print("  ✅ All pending Slack notifications sent!")
        
    print("\n🎯 Daily Operation Fully Completed.")

if __name__ == "__main__":
    main()
