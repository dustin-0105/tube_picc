#!/bin/bash
# ---------------------------------------------------------
# YouTube Curation Bot - Automated Cron Execution Script
# ---------------------------------------------------------

# 1. 터미널 경로가 달라도 안전하게 실행될 수 있도록 디렉토리 이동
cd "/Users/dustin/Antigravity PJ/edu_youtube_curator"

# 2. 크론 스케줄러의 빈약한 초깃값(PATH)에 Node.js 및 기본 명령어 경로들 주입
# NLM 등 CLI 도구들이 정상 작동하기 위해 매우 중요합니다.
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$PATH"

# 3. 파이썬 가상환경(venv) 켜기
source venv/bin/activate

# 4. 봇 실행 및 로그 파일 기록
# - 날짜와 시간을 기록하고 봇을 돌립니다.
# - 모든 에러와 출력 화면을 cron.log 파일에 누적 저장합니다.
echo "=====================================" >> cron.log
echo "봇 가동 시작: $(date)" >> cron.log
echo "=====================================" >> cron.log

python3 main.py >> cron.log 2>&1

echo "봇 가동 종료: $(date)" >> cron.log
echo "" >> cron.log
