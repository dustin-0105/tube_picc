import os
import re
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
import google.generativeai as genai
import config
from sheets_manager import get_curated_video_ids

def get_youtube_client():
    """Initialize the YouTube Data API v3 client."""
    api_key = config.YOUTUBE_API_KEY
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is not set in the environment.")
    return build("youtube", "v3", developerKey=api_key)

def parse_duration(pt_duration_str):
    """
    Parses ISO 8601 duration string (e.g., 'PT15M33S') into total minutes.
    """
    if not pt_duration_str:
        return 0
    
    hours_match = re.search(r'(\d+)H', pt_duration_str)
    mins_match = re.search(r'(\d+)M', pt_duration_str)
    secs_match = re.search(r'(\d+)S', pt_duration_str)
    
    hours = int(hours_match.group(1)) if hours_match else 0
    mins = int(mins_match.group(1)) if mins_match else 0
    secs = int(secs_match.group(1)) if secs_match else 0
    return hours * 60 + mins + secs / 60.0

def select_fresh_video_with_ai(candidates, past_titles, content_target):
    """
    Uses Gemini AI to play the role of an editor preventing semantic duplicates.
    It selects the index of the most fresh and appropriate video from the candidates list.
    """
    # If no past titles, or only 1 candidate, just pick the first one (most views as sorted)
    if not candidates:
        return None
    if len(candidates) == 1 or not past_titles:
        return candidates[0]
        
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    # Safely truncate past titles if too many to fit in context window nicely
    safe_past_titles = past_titles[-20:] # Last 20 recommended titles
    past_titles_str = "\n".join(f"- {title}" for title in safe_past_titles)
    
    candidates_str = ""
    for i, c in enumerate(candidates):
        candidates_str += f"[{i+1}] 제목: {c['title']} | 업로드일: {c.get('published_at', 'Unknown')} | 설명: {c.get('description', '')[:50]}... | 조회수: {c['view_count']}\n"
        
    prompt = f"""
당신은 유튜브 콘텐츠 큐레이션을 결정하는 전문 편집장(Editor in Chief)입니다.
우리의 목표 구독자들은 다음과 같은 타겟 영상을 원합니다.
[목표 타겟]: {content_target}

아래는 [최근에 이미 추천 발송된 과거 영상 제목 목록]입니다.
{past_titles_str}

그리고 아래는 [오늘 유튜브에서 새롭게 찾아낸 후보 영상 TOP 10]입니다.
{candidates_str}

[당신의 임무]
과거에 추천했던 영상 제목들을 잘 분석하세요. 오늘 새롭게 추천할 영상은 '과거 추천 내용과 뻔하게 겹치지 않으면서(신선한 각도)', 목표 타겟에 부합하고, 조회수도 높은 훌륭한 영상이어야 합니다.
특히 최근 1주일(7일) 이내에 업로드된 최신 트렌드 영상이 있다면 높은 가산점을 주고 우선적으로 선발하세요.
가장 완벽한 딱 1개의 영상 번호(1~{len(candidates)})를 찾아내세요.

주의: 반드시 오직 숫자(예: 3) 하나만 응답해야 합니다. 다른 말이나 부가 설명은 일절 금지합니다.
"""
    try:
        response = model.generate_content(prompt)
        # Parse the raw number from text
        match = re.search(r'\d+', response.text)
        if match:
            idx = int(match.group()) - 1
            if 0 <= idx < len(candidates):
                print(f"  🧠 AI Editor selected candidate [{idx+1}]: {candidates[idx]['title']}")
                return candidates[idx]
                
        print(f"  ⚠️ AI Editor returned unparsable response: {response.text}")
    except Exception as e:
        print(f"  ⚠️ AI Editor selection failed: {e}")
        
    # Fallback to the Top 1 (highest views)
    print(f"  💡 Falling back to the most viewed candidate.")
    return candidates[0]

def generate_search_queries(content_target):
    """
    Uses Gemini AI to generate 3 optimized YouTube search queries based on the user's content target.
    """
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    prompt = f"""
다음은 사용자가 유튜브에서 찾고 싶어하는 콘텐츠에 대한 상세 설명입니다.
[사용자 설명]: "{content_target}"

이 설명을 바탕으로, 유튜브 검색창에 입력했을 때 가장 정확하고 고품질의 한국어 영상을 찾아낼 수 있는 '유튜브 검색용 키워드(Query)' 딱 5개만 추천해주세요.
반드시 쉼표(,)로만 구분해서 출력하세요. 다른 말은 절대 금지.
예시: 엑셀 매크로 기초,직장인 엑셀 자동화 튜토리얼,엑셀 VBA 실무,엑셀 실무 꿀팁,엑셀 매크로 만들기
"""
    try:
        response = model.generate_content(prompt)
        queries = response.text.strip().split(',')
        return [q.strip() for q in queries if q.strip()][:5]
    except Exception as e:
        print(f"⚠️ Query generation failed: {e}")
        # Fallback query if AI fails
        return [content_target[:50]]

def get_strictly_related_videos(youtube, featured_title, featured_id, max_age_days):
    """
    Performs a targeted YouTube search using the featured video's title 
    to find highly relevant subsequent content, avoiding generic broad topic results.
    """
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    published_after = cutoff_date.isoformat().replace("+00:00", "Z")
    
    related = []
    try:
        search_response = youtube.search().list(
            q=featured_title,
            part="id,snippet",
            type="video",
            maxResults=5,
            publishedAfter=published_after,
            relevanceLanguage="ko" 
        ).execute()
        
        for item in search_response.get("items", []):
            v_id = item["id"]["videoId"]
            if v_id != featured_id:
                related.append({
                    "video_id": v_id,
                    "title": item["snippet"]["title"],
                    "channel_name": item["snippet"]["channelTitle"],
                    "url": f"https://www.youtube.com/watch?v={v_id}"
                })
            if len(related) >= 3:
                break
    except Exception as e:
        print(f"  ⚠️ Failed to fetch strictly related videos: {e}")
        
    return related

def search_educational_videos(topic_name, content_target, max_age_days=365, past_titles=None):
    """
    Searches YouTube for videos matching the topic, filters by criteria,
    and returns 1 featured video and up to 3 related videos.
    """
    youtube = get_youtube_client()
    
    # 1. Calculate cutoff date format: YYYY-MM-DDThh:mm:ssZ
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    published_after = cutoff_date.isoformat().replace("+00:00", "Z")
    
    # 2. Get AI-optimized search queries
    print(f"  🧠 AI is brainstorming search queries for: '{content_target}'...")
    queries = generate_search_queries(content_target)
    print(f"  🔍 Generated Queries: {queries}")
    
    # 3. Search for videos across all queries
    video_ids = []
    
    for q in queries:
        try:
            search_response = youtube.search().list(
                q=q,
                part="id,snippet",
                type="video",
                maxResults=20, # 20 per query (total up to 60)
                publishedAfter=published_after,
                relevanceLanguage="ko" 
            ).execute()
            
            items = search_response.get("items", [])
            for item in items:
                video_ids.append(item["id"]["videoId"])
        except Exception as e:
            print(f"  ⚠️ Search failed for query '{q}': {e}")
            
    # Remove duplicate video IDs
    video_ids = list(set(video_ids))
    
    if not video_ids:
        return None, []
        
    # Chunk the IDs for videos().list (max 50 at a time)
    video_ids = video_ids[:50]
    
    # 3. Get detailed video metadata (duration, statistics)
    videos_response = youtube.videos().list(
        part="contentDetails,statistics,snippet",
        id=",".join(video_ids)
    ).execute()
    
    video_details = videos_response.get("items", [])
    
    # Extract unique channel IDs
    channel_ids = list(set([vid["snippet"]["channelId"] for vid in video_details]))
    
    # 4. Get channel details to fetch subscriber counts
    channels_response = youtube.channels().list(
        part="statistics",
        id=",".join(channel_ids)
    ).execute()
    
    channel_stats = {}
    for ch in channels_response.get("items", []):
        channel_stats[ch["id"]] = int(ch.get("statistics", {}).get("subscriberCount", 0))
        
    # 5. Filter the videos based on quantitative criteria and history
    valid_videos = []
    min_subs = config.DEFAULT_MIN_SUBSCRIBERS
    min_dur = config.DEFAULT_MIN_DURATION_MINS
    max_dur = config.DEFAULT_MAX_DURATION_MINS
    
    curated_ids = get_curated_video_ids()
    print(f"  📚 Found {len(curated_ids)} videos in curation history.")
    
    for vid in video_details:
        channel_id = vid["snippet"]["channelId"]
        subs = channel_stats.get(channel_id, 0)
        # Graceful fallback for missing contentDetails or duration
        content_details = vid.get("contentDetails", {})
        duration_str = content_details.get("duration", "PT0M")
        duration_mins = parse_duration(duration_str)
        
        video_id = vid["id"]
        
        # Hard filters + Duplicate check
        if subs >= min_subs and min_dur <= duration_mins <= max_dur:
            if video_id not in curated_ids:
                valid_videos.append({
                    "video_id": video_id,
                    "title": vid["snippet"]["title"],
                    "channel_name": vid["snippet"]["channelTitle"],
                    "duration_mins": round(duration_mins),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "published_at": vid["snippet"]["publishedAt"],
                    "description": vid["snippet"]["description"],
                    "view_count": int(vid.get("statistics", {}).get("viewCount", 0))
                })
            
    if not valid_videos:
        # None met criteria
        return None, []
        
    # 6. Sort valid videos by view_count to establish a baseline top list
    valid_videos.sort(key=lambda x: x["view_count"], reverse=True)
    
    # 7. Use AI Editor to pick the featured video ensuring semantic freshness
    print(f"  🤖 Invoking AI Editor to select the best fresh video out of {len(valid_videos)} candidates...")
    top_candidates = valid_videos[:10] # Give AI the top 10 most popular ones to choose from
    featured = select_fresh_video_with_ai(top_candidates, past_titles, content_target)
    
    if featured:
        print(f"  🔍 Fetching strictly related videos for '{featured['title'][:30]}...'")
        related = get_strictly_related_videos(youtube, featured['title'], featured['video_id'], max_age_days)
        if not related:
            # Fallback to the broad search pool if targeted search fails
            related = [v for v in valid_videos if v["video_id"] != featured["video_id"]][:3]
    else:
        related = []
    
    return featured, related

if __name__ == "__main__":
    # ---------------------------------------------------------
    # INDEPENDENT TEST BLOCK
    # Run this file directly to test the YouTube search & filter
    # ---------------------------------------------------------
    print("Testing youtube_search.py...")
    try:
        topic = "AI Tools"
        target = "직장인이 당장 쓸 수 있는 챗GPT 실무 활용법"
        max_age = 180
        print(f"Searching for Topic: '{topic}' - '{target}'\n")
        
        featured, related = search_educational_videos(topic, target, max_age_days=max_age)
        
        if featured:
            print("✅ [FEATURED VIDEO]")
            print(f"Title   : {featured['title']}")
            print(f"Channel : {featured['channel_name']}")
            print(f"Duration: {featured['duration_mins']} mins")
            print(f"Views   : {featured['view_count']}")
            print(f"URL     : {featured['url']}\n")
            
            print("✅ [RELATED VIDEOS]")
            for r in related:
                print(f"- {r['title']} | {r['channel_name']} | {r['url']}")
        else:
            print("❌ No videos found matching the criteria (10k+ subs, 5-30 mins).")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Ensure that your YOUTUBE_API_KEY is correctly set in the .env file!")
