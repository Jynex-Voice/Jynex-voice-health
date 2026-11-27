from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.agora_service import generate_rtc_token
from app.llm_medical import generate_medical_response
from app.tts_router import synthesize_speech

load_dotenv()

app = FastAPI(title="Jynex Voice Health API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSION_HISTORY: dict[str, list[dict]] = {}

class VoiceChatRequest(BaseModel):
    session_id: str = "default"
    transcript: str

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Jynex Voice Health Backend"}

@app.get("/api/token")
def get_agora_token(channel: str = "jynex-room", uid: int = 0):
    return generate_rtc_token(channel_name=channel, uid=uid)

@app.post("/api/chat/voice")
async def voice_chat(req: VoiceChatRequest):
    history = SESSION_HISTORY.setdefault(req.session_id, [])
    llm_data = await generate_medical_response(req.transcript, history)

    history.append({"role": "user", "content": req.transcript})
    history.append({"role": "assistant", "content": llm_data["reply_text"]})

    tts_data = await synthesize_speech(
        text=llm_data["reply_text"],
        language=llm_data.get("language", "hi"),
    )

    return {
        "reply_text": llm_data["reply_text"],
        "language": llm_data.get("language", "hi"),
        "tts_engine_used": tts_data["tts_engine_used"],
        "audio_base64": tts_data["audio_base64"],
        "medicine_cards": llm_data.get("medicine_cards", []),
        "doctor_summary": llm_data.get("doctor_summary"),
    }