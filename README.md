# 🚀 텔레그램 AI 자동 답장 중계 서버 (Render 무료 배포 가이드)

이 프로젝트는 텔레그램 단톡방에서 **뮤즈봇(Muse)**이 메시지를 남기면, 0.1초 만에 웹훅으로 감지하여 **피클이봇**이 자동으로 실시간 답장을 보내도록 만들어진 24시간 상시 중계 서버입니다.

---

## 🛠️ 배포 방법 (5분 완성)

### 1단계: Render.com 가입 및 로그인
1. [Render.com](https://render.com) 접속
2. 우측 상단 **"GET STARTED"** 또는 **"Sign in"** 클릭
3. **"GitHub" 아이콘**을 눌러 기존 GitHub 계정으로 1초 로그인

### 2단계: 새 웹 서비스 생성 (New Web Service)
1. Render 대시보드에서 **"New +"** 버튼 클릭 → **"Web Service"** 선택
2. **"Build and deploy from a Git repository"** 선택 후 GitHub 저장소 연결
3. 설정값 입력:
   - **Name**: `my-pickle-relay` (원하는 이름 아무거나)
   - **Region**: `Singapore` (한국과 가장 가까움)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free ($0/month)** 선택!

### 3단계: 환경변수 설정 (선택 사항)
- **Environment Variables** 탭에서 아래 항목 추가 가능:
  - `TELEGRAM_BOT_TOKEN`: 피클이 봇 토큰 (기본값 내장되어 있음)
  - `TARGET_CHAT_ID`: 단톡방 번호 (`-5144564831`)
  - `AI_API_KEY`: (선택) OpenAI, Grok 등 API 키를 넣으면 최첨단 LLM이 실시간 답변 생성

### 4단계: 배포 시작 (Deploy Web Service)
- 화면 맨 아래 **"Deploy Web Service"** 클릭!
- 약 1~2분 후 화면 상단에 초록색 불이 들어오며 고유 주소가 생성됩니다:
  `https://my-pickle-relay.onrender.com`

---

## 🔗 5단계: 텔레그램에 웹훅 등록 (마지막 10초)

웹 브라우저(크롬, 사파리 등) 주소창에 아래 한 줄을 그대로 복사해서 엔터를 칩니다:

```text
https://api.telegram.org/bot9183049769:AAGFoMP_KBxP6JzQYb5QJ0LjNHzP1CUBHME/setWebhook?url=https://[내-Render-주소].onrender.com/webhook
```
*(예: `url=https://my-pickle-relay.onrender.com/webhook`)*

화면에 `{"ok":true,"result":true,"description":"Webhook was set"}`가 뜨면 모든 세팅 완료! 🎉

이제부터는 문정 님이 피클 앱을 열지 않아도, 텔레그램 방에서 뮤즈봇이 글을 쓰면 1초 만에 피클이 봇이 척척 자동으로 실시간 대화를 나눕니다.
