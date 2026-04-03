# YouTube Content Curation Bot (tube_picc)

사원들의 역량 강화를 위한 사내 교육용 YouTube 콘텐츠 자동 큐레이션, 요약 및 팟캐스트 변환 봇입니다. 

## 1. 프로젝트 소개
이 프로젝트는 구글 스프레드시트에 기입된 주제(Topic)에 맞는 고품질 YouTube 영상을 주기적으로 탐색하여, Gemini API를 통해 내용을 요약하고 Google Docs로 변환합니다. 최종적으로 **NotebookLM**을 활용해 오늘 수집된 모든 정보들을 취합한 **'데일리 오디오 팟캐스트'**를 생성한 뒤 Slack으로 팀원들에게 자동 공유하는 완전 무인 자동화 파이프라인입니다.

## 2. 주요 기능 및 파이프라인
- **동적 주제 검색 및 이력 관리:** Google Sheets 기반으로 주제를 유연하게 추가/수정하며, 이미 추천된 영상은 AI가 분석하여 중복 추천을 방지합니다.
- **AI 맞춤형 편집장:** 유튜브 검색 결과를 바탕으로 Gemini AI가 최신 트렌드를 반영한 가장 적합한 단 1개의 영상을 골라냅니다.
- **마크다운(Markdown) 자동화 문서:** 추출된 자막과 요약본을 마크다운 양식으로 가공하여, 깔끔한 디자인의 Google Docs 문서로 찍어냅니다.
- **NotebookLM 팟캐스트 자동 생성:** 여러 주제의 요약 문서와 원본 유튜브 영상을 NotebookLM에 학습시켜, 라디오 형식의 고품질 한국어 오디오 팟캐스트를 생성합니다.
- **슬랙(Slack) 전송 예약 시스템:** 팟캐스트 제작이 모두 완료될 때까지(최대 30분) 개별 알림을 보류했다가, 제작 완료 즉시 개별 요약본과 팟캐스트를 한 번에 슬랙으로 쏴줍니다.

## 3. 전체 구조 설명
- `main.py`: 전체 흐름을 제어하는 진입점 (설정된 주제에 대해 탐색 -> 요약 -> 팟캐스트 생성 -> 공유 동작)
- `config.py`: 환경 변수(`.env`) 로드 및 하드코딩 설정 값 관리
- `sheets_manager.py`: Google Sheets 데이터(주제 목록 및 중복 방지 이력) 읽기 및 쓰기 담당
- `youtube_search.py`: YouTube API 조회 및 Gemini AI 기반 정밀 타겟팅 검색, 유사 콘텐츠 추출
- `summarizer.py`: YouTube 자막 추출 및 Gemini AI를 통한 상세 내용 요약
- `docs_manager.py`: Markdown -> HTML 렌더링을 통한 Google Docs 생성
- `drive_manager.py`: 파일(오디오, 오버뷰 등)을 특정 Google Drive 폴더로 안전하게 업로드 및 공유 권한 제어
- `notebooklm_manager.py`: NotebookLM CLI(`nlm`)를 활용하여 다중 소스 병합 및 오디오(팟캐스트) 생성 통제
- `slack_notifier.py`: 작성된 문서 링크 및 오디오 팟캐스트 링크를 Slack Webhook으로 일괄 발송 
- `run_bot.sh`: `cron` 등 백그라운드 환경에서도 환경 변수를 잃지 않고 구동시키기 위한 쉘 스크립트

## 4. 사전 준비 (API 키 발급 방법)
아래 인증 정보가 필요합니다. 발급받은 키는 루트 경로의 `.env` 파일에 저장해야 합니다.

* **YouTube Data API v3:** [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트 생성, API 사용 설정.
* **Gemini API:** [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급.
* **Slack Webhook URL:** Slack 워크스페이스 앱에서 타겟 채널 지정 후 URL 획득.
* **Google Service Account (.json):** [Google Cloud Console](https://console.cloud.google.com/)에서 키 다운로드. **Google Docs, Drive, Sheets API** 권한이 활성화되어 있어야 합니다.
* **NotebookLM CLI:** 로컬 PC에 글로벌로 설치된 `notebooklm-mcp-cli` (`npm install -g notebooklm-mcp-cli` 이후 `nlm login` 필수).

## 5. 설치 및 실행 방법

### 환경 설정
1. 저장소 클론 후 폴더 이동
2. 가상 환경 생성 및 진입
```bash
python3 -m venv venv
source venv/bin/activate
```
3. 의존성 설치
```bash
pip install -r requirements.txt
```
4. `.env.example` 복사 후 `.env` 생성 (폴더 ID 및 API 키 세팅)

### 구동 및 자동화
```bash
# 직접 1회 실행
python3 main.py

# Cron을 이용한 자동화 스케줄링 가동을 위한 권한 부여
chmod +x run_bot.sh
```

## 6. 핵심 프롬프트 수정
요약투나 팟캐스트의 진행 방식을 바꾸고 싶다면 아래를 수정하세요.
- 비디오 요약: `prompts/summarize.txt`
- 팟캐스트 형식: `notebooklm_manager.py`의 `custom_focus` 텍스트 수정

## 7. 기여 방법
이슈와 Pull Request를 언제든 환영합니다! 버그 리포트, 기능 제안 등은 GitHub Issues 메뉴에 자유롭게 남겨주세요.
