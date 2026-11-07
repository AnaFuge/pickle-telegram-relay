import os
import time
import requests
from fastapi import FastAPI, Request

app = FastAPI(title="Pickle-Muse Telegram Relay")

# 환경변수에서 설정 로드 (Render 대시보드에서 등록 가능)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID", "-5144564831")
AI_API_KEY = os.getenv("AI_API_KEY", "")  # OpenAI, Grok, Gemini 등 (선택)

# 중복 처리 방지용 캐시
processed_updates = set()

def send_telegram_message(chat_id: str, text: str):
    """피클이 봇으로 텔레그램 방에 메시지 전송"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"[피클이]\n{text}"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.json()
    except Exception as e:
        print(f"전송 실패: {e}")
        return None

def generate_ai_reply(prompt: str) -> str:
    """AI API가 설정되어 있으면 호출 (Google Gemini 또는 OpenAI 자동 감지)"""
    if AI_API_KEY:
        try:
            # 1. Google Gemini API (키가 AIza로 시작)
            if AI_API_KEY.startswith("AIza"):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"너는 개인 비서 AI '피클이'야. 사용자는 문정 님이야. 텔레그램 토론방에서 뮤즈봇의 의견이나 문정 님의 메시지에 대해 팩트와 데이터를 바탕으로 밝고 예의 바르게 2~4줄로 핵심만 답장해줘.\n\n상대방 메시지: {prompt}"
                        }]
                    }]
                }
                res = requests.post(url, json=payload, timeout=10).json()
                return res["candidates"][0]["content"]["parts"][0]["text"]
            
            # 2. OpenAI API (sk- 로 시작)
            else:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {AI_API_KEY}"}
                data = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "너는 개인 비서 AI '피클이'야. 사용자는 문정 님이야. 텔레그램 토론방에서 뮤즈봇이나 문정 님의 말에 대해 팩트와 금융 데이터를 바탕으로 밝고 정중하게 2~4줄로 답장해."
                        },
                        {"role": "user", "content": prompt}
                    ]
                }
                res = requests.post(url, headers=headers, json=data, timeout=15).json()
                return res["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"AI API 호출 오류: {e}")
    
    # API 키가 없을 때 기본 템플릿
    return f"뮤즈봇 님의 말씀 잘 들었습니다! 말씀해 주신 내용('{prompt[:40]}...')에 대해 백테스트 수치와 퀀트 지표를 대조하여 추가 분석을 진행하겠습니다. 문정 님의 자산 방어를 최우선으로 검토할게요."

@app.get("/")
def health_check():
    """서버 생존 확인용 (Render 헬스체크)"""
    return {"status": "ok", "service": "Telegram Relay Server", "time": time.time()}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """텔레그램에서 실시간 메시지가 들어올 때 0.1초 만에 호출되는 엔드포인트"""
    data = await request.json()
    
    update_id = data.get("update_id")
    if not update_id or update_id in processed_updates:
        return {"ok": True}
    
    # 최근 500개 update_id 기억 (중복 방지)
    processed_updates.add(update_id)
    if len(processed_updates) > 500:
        processed_updates.pop()
    
    message = data.get("message", {})
    chat_id = str(message.get("chat", {}).get("id"))
    sender = message.get("from", {})
    sender_username = sender.get("username", "")
    text = message.get("text", "")
    
    # 내가 보낸 메시지 무시 (무한 루프 방지)
    if sender_username == "my_pickle_agent_bot":
        return {"ok": True}
    
    # 뮤즈봇이 보낸 메시지 감지
    if sender_username == "my_loyal_muse_agent_bot" or "/토론" in text or "@my_pickle_agent_bot" in text:
        print(f"[수신] {sender_username}: {text}")
        
        # 답장 생성
        reply_text = generate_ai_reply(text)
        
        # 텔레그램 방으로 즉시 자동 답장 전송
        send_telegram_message(chat_id, reply_text)
    
    return {"ok": True}
