# YouTube Content Curation Bot

사원들의 역량 강화를 위한 사내 교육용 YouTube 콘텐츠 큐레이션 및 요약 봇입니다. 

## 1. 프로젝트 소개
이 프로젝트는 특정 주제(예: AI Tools, Investment 등)에 맞는 고품질 YouTube 영상을 주기적으로 탐색하여, Gemini API를 통해 내용을 요약하고 Google Docs에 저장한 뒤 Slack으로 팀원들에게 공유하는 자동화 파이프라인입니다.

## 2. 전체 구조 설명
- `main.py`: 전체 흐름을 제어하는 진입점 (설정된 주제에 대해 탐색 -> 요약 -> 공유 동작)
- `config.py`: 환경 변수(`.env`) 로드 및 하드코딩된 주제(Phase 1) 설정 값 관리
- `youtube_search.py`: YouTube Data API v3를 활용한 영상 검색, 필터링 및 정렬 수행 (메인 영상 1개, 관련 영상 최대 3개)
- `summarizer.py`: YouTube 자막 추출 및 Gemini API를 통한 내용 요약. `prompts/summarize.txt`를 기반으로 답변 생성
- `docs_manager.py`: Google Docs를 생성하여 전체 요약문 삽입 및 Google Drive 공유 속성(누구에게나 공개) 적용
- `slack_notifier.py`: 작성된 문서 링크 및 관련 영상 정보 등을 조합해 Slack Webhook으로 메시지 발송 
- `prompts/summarize.txt`: 프롬프트 문서. 코드를 고치지 않아도 요약 지시사항을 변경할 수 있도록 분리됨.

## 3. 사전 준비 (API 키 발급 방법)
아래 4가지 인증 정보가 필요합니다. 발급받은 키는 프로젝트 루트 경로의 `.env` 파일에 저장해야 합니다.

* **YouTube Data API v3:** [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트를 생성하고, API 사용 설정 후 사용자 인증 정보에서 API 키 발급.
* **Gemini API:** [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급.
* **Slack Webhook URL:** Slack 워크스페이스에서 `Incoming WebHooks` 앱을 추가하고, 포스팅할 채널을 지정하여 URL 주소 획득.
* **Google Service Account (.json):** [Google Cloud Console](https://console.cloud.google.com/)에서 서비스 계정을 생성하고 키 파일(JSON) 생성 후 다운로드. 이 프로젝트 계정에는 **Google Docs API** 및 **Google Drive API** 권한이 활성화되어 있어야 합니다.

## 4. 설치 및 실행 방법

### 환경 설정
1. 저장소 클론 후 폴더 이동
2. 가상 환경 생성 및 진입
```bash
python3 -m venv venv
source venv/bin/activate  # Mac / Linux
```
3. 의존성 설치
```bash
pip install -r requirements.txt
```
4. 시작하기 전에 `.env.example` 파일을 복사하여 `.env` 파일을 만들고 키 정보를 기입합니다.
```bash
cp .env.example .env
```
(`GOOGLE_SERVICE_ACCOUNT_JSON` 값은 다운로드 받은 `service_account.json` 파일의 경로/이름으로 지정)

### 실행
```bash
python3 main.py
```

## 5. 프롬프트 수정 방법
비개발자도 쉽게 AI의 출력 스타일을 바꿀 수 있습니다. `prompts/summarize.txt` 파일을 열고 지시사항과 작성 규칙을 변경한 뒤, 스크립트를 재실행하기만 하면 됩니다.

## 6. Phase 2 예정 기능 (Future Scope)
향후 버전(Phase 2)에서는 다음 기능들이 추가될 예정입니다.
- **Google Sheets 연동:** 스크립트 내부 설정(`config.py`) 대신, 스프레드시트에서 검색할 주제와 주제별(Topic) 프롬프트를 직관적으로 관리할 수 있게 됩니다.
- **중복 방지 이력 관리:** Sheets의 별도 탭에 이력이 기록되어 예전에 보내진 영상은 자동 제외됩니다.
- **자동화(Scheduler) 설정:** macOS `cron` 등을 이용하여 백그라운드에서 주기적으로 (예: 매주 월요일 아침) 요약본이 생성 및 배포되도록 구성됩니다.

## 7. 기여 방법
이슈와 Pull Request를 언제든 환영합니다! 버그 리포트, 기능 제안 등은 GitHub Issues 메뉴에 자유롭게 남겨주세요.
