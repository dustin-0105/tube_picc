import subprocess
import time
import os
import re
from datetime import datetime
import config

NLM_CLI = os.getenv("NLM_CLI_PATH", "nlm")

def run_cli(command_list):
    """Executes a CLI command and returns the stdout output."""
    cmd = [NLM_CLI] + command_list
    print(f"Running NLM Command: {' '.join(cmd)}")
    
    # We pipe stdin from /dev/null so interactive prompts fail/fallback instead of blocking
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        print(f"NLM Error: {result.stderr}")
        return None
        
    return result.stdout.strip()

def extract_id(output_text, prefix="ID:"):
    """Helper to extract UUIDs from CLI outputs."""
    if not output_text: return None
    
    match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', output_text)
    if match:
        return match.group(1)
    return None

def create_daily_audio_overview(doc_urls, youtube_urls):
    """
    Orchestrates the NLM CLI to generate a unified audio podcast
    based on the curated results of the day.
    
    It will:
    1. Create a Notebook
    2. Add Youtube & Docs links as sources
    3. Trigger a Podcast Generation Job
    4. Wait up to 10 minutes for it to finish
    5. Download to a local location
    
    Returns the local file path to the audio file if successful, or None.
    """
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    notebook_name = f"[{today_str}] 데일리 큐레이션 통합본"
    
    print(f"\n🎧 Initiating AI Audio Podcast Pipeline: '{notebook_name}'")
    
    # 1. Create Notebook
    create_out = run_cli(["create", "notebook", notebook_name])
    notebook_id = extract_id(create_out)
    
    if not notebook_id:
        print("❌ Failed to create NotebookLM notebook.")
        return None
        
    print(f"✅ Notebook created: {notebook_id}")
    
    # 2. Add Sources
    # Add Google Docs links
    for doc in doc_urls:
        print(f"  > Adding Google Doc Source...")
        run_cli(["source", "add", notebook_id, "--url", doc, "--wait"])
        
    # Add YouTube videos
    for yt in youtube_urls:
        print(f"  > Adding Youtube Source...")
        run_cli(["source", "add", notebook_id, "--url", yt, "--wait"])
        
    print("✅ All sources added successfully.")
    
    # 3. Create Audio Job
    custom_focus = (
        "각각의 주제에 대한 유투브 영상과 이를 요약한 문서가 있는데, 서로 다른 주제들을 다루고 있어. "
        "각 주제를 별도 섹션으로 소개하고 억지로 연결하지 마. "
        "두 진행자가 각 주제를 독립적인 코너로 나눠서 진행해줘."
    )
    audio_cmd = [
        "audio", "create", notebook_id, 
        "--format", "deep_dive", 
        "--language", "ko",
        "--length", "default",
        "--focus", custom_focus,
        "--confirm"
    ]
    
    audio_out = run_cli(audio_cmd)
    
    # Check if started successfully
    # Note: audio create output says "Artifact ID: <uuid>"
    artifact_id = extract_id(audio_out)
    print(f"✅ Audio generation job triggered. Artifact ID: {artifact_id}")
    
    # 4. Polling for Completion (Max 30 minutes)
    max_retries = config.NLM_POLL_MAX_RETRIES
    retry_count = 0

    audio_ready = False
    timeout_mins = (max_retries * config.NLM_POLL_INTERVAL_SECS) // 60
    print(f"⏳ Waiting for audio generation (Timeout: {timeout_mins} mins)...")
    
    # Check status endpoint with --json or grep
    # NLM studio status lists artifacts
    while retry_count < max_retries:
        status_out = run_cli(["studio", "status", notebook_id])
        if status_out:
            # simple check for artifact ID and completed text
            # Depending on cli output format, usually if completed we should see it
            # The nlm studio status returns JSON structure visually in raw text or a rich table. 
            # Easiest way is to just grep "completed" near the artifact ID, but status CLI is dynamic.
            if artifact_id and artifact_id in status_out and "completed" in status_out.lower():
                audio_ready = True
                print("\n✅ Audio generation COMPLETED!")
                break
            elif "in_progress" in status_out.lower():
                print(".", end="", flush=True)
            elif "failed" in status_out.lower():
                print("\n❌ Audio generation FAILED on NotebookLM side.")
                break
        
        time.sleep(config.NLM_POLL_INTERVAL_SECS)
        retry_count += 1
        
    if not audio_ready:
        print("\n⏳ Audio generation timed out or failed. Skipping Podcast generation.")
        print(f"💡 Notebook remains intact. You can check progress at notebooklm.google.com! (ID: {notebook_id})")
        # run_cli(["delete", "notebook", notebook_id, "--confirm"])
        return None
        
    # 5. Download Audio
    output_audio_path = f"/tmp/ai_podcast_{today_str}.wav"
    print(f"⬇️ Downloading generated audio to {output_audio_path}")
    
    # The output from "download audio" drops it on disk
    download_cmd = [
        "download", "audio", notebook_id,
        "--id", artifact_id,
        "--output", output_audio_path
    ]
    
    run_cli(download_cmd)
    
    # Cleanup notebook space after downloading
    print("🧹 Cleaning up temporary notebook...")
    run_cli(["delete", "notebook", notebook_id, "--confirm"])
    
    if os.path.exists(output_audio_path):
        return output_audio_path
        
    print("❌ Download command completed but file is missing locally.")
    return None
