import os
import requests
import config

def extract_key_points(summary_text):
    """
    Extracts the bullet points under '## 핵심 요약' from the Gemini summary.
    If it fails to parse, it returns a generic fallback string.
    """
    try:
        # Split by '## ' to find the section
        parts = summary_text.split("## ")
        for part in parts:
            if part.startswith("핵심 요약"):
                # Return everything after "핵심 요약\n"
                lines = part.split("\n")[1:]
                # Filter out empty lines
                return "\n".join([line for line in lines if line.strip()]).strip()
    except Exception as e:
        print(f"Warning: Failed to extract key points: {e}")
        
    return "- 주요 요약 내용을 찾을 수 없습니다.\n- 전체 요약 페이지를 확인해 주세요."

def send_slack_message(topic_name, featured_video, doc_url, summary_text):
    """
    Constructs the formatted Slack message and sends it to the Webhook URL.
    """
    webhook_url = config.SLACK_WEBHOOK_URL
    if not webhook_url:
        print("💡 SLACK_WEBHOOK_URL is not set. Skipping Slack notification.")
        return False
        
    key_points = extract_key_points(summary_text)
    
    # Construct Message Text using Slack markdown syntax
    message_text = (
        f"—\n"
        f"📚 *이번 주 추천 콘텐츠* | {topic_name}\n\n"
        f"🎬 *{featured_video['title']}*\n"
        f"📺 {featured_video['channel_name']} | ⏱️ {featured_video['duration_mins']}분\n"
        f"🔗 <{featured_video['url']}|유튜브에서 보기> | 📄 <{doc_url}|상세 요약 보기>\n\n"
        f"📝 *핵심 내용*\n"
        f"{key_points}\n\n"
        f"—"
    )
    
    payload = {
        "text": message_text
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Slack message: {e}")
        return False

def send_daily_audio_message(audio_url):
    """
    Sends the aggregated daily Audio Podcast link to Slack.
    """
    webhook_url = config.SLACK_WEBHOOK_URL
    if not webhook_url:
        return False
        
    message_text = (
        f"🎙️ *[오늘의 큐레이션 통합 팟캐스트가 완성되었습니다]*\n\n"
        f"오늘 수집된 모든 교육 영상과 요약 문서를 바탕으로 AI 오디오 브리핑이 생성되었습니다.\n"
        f"출근길, 이동 중에 귀로 들으며 빠르게 트렌드를 파악해 보세요!\n\n"
        f"🎧 <{audio_url}|AI 오디오 브리핑 듣기 (Google Drive)>\n"
        f"—"
    )
    
    payload = {"text": message_text}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Audio Slack message: {e}")
        return False

if __name__ == "__main__":
    # ---------------------------------------------------------
    # INDEPENDENT TEST BLOCK
    # ---------------------------------------------------------
    print("Testing slack_notifier.py...")
    try:
        test_topic = "AI Tools"
        test_featured = {
            "title": "ChatGPT 실무 활용의 모든 것",
            "channel_name": "Antigravity AI Trend",
            "duration_mins": 15,
            "url": "https://youtube.com/watch?v=featured"
        }
        test_doc = "https://docs.google.com/document/d/123/edit"
        
        # Simulating Gemini's output
        test_summary = (
            "## 핵심 요약\n"
            "- ChatGPT의 기본 활용법을 익히고 실무 효율을 높입니다.\n"
            "- 프롬프트 엔지니어링의 기초와 원리를 깨닫습니다.\n"
            "- 실무에 바로 적용 가능한 3가지 구체적 예제를 살펴봅니다.\n\n"
            "## 상세 내용\n"
            "이곳에는 자세한 내용이 들어갑니다."
        )
        
        print("Sending message to Slack Webhook...")
        success = send_slack_message(test_topic, test_featured, test_doc, test_summary)
        
        if success:
            print("\n✅ Slack message sent successfully! Check your channel.")
        else:
             print("\n⚠️ Message was not sent. Check if SLACK_WEBHOOK_URL is set.")
    except Exception as e:
        print(f"❌ Error during test: {e}")
