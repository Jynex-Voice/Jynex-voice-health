import os
import httpx

SARVAM_LANG_MAP = {
    "hi": "hi-IN",
    "gu": "gu-IN",
    "mr": "mr-IN",
}

async def synthesize_speech(text: str, language: str) -> dict:
    sarvam_key = os.getenv("SARVAM_API_KEY", "").strip()
    murf_key = os.getenv("MURF_API_KEY", "").strip()

    # Route 1: Indian Regional Languages -> Sarvam AI Bulbul v2 TTS
    if language in SARVAM_LANG_MAP:
        if not sarvam_key or "your_" in sarvam_key:
            return {"tts_engine_used": "sarvam_mock", "audio_base64": None}

        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.post(
                "https://api.sarvam.ai/text-to-speech",
                headers={"api-subscription-key": sarvam_key, "Content-Type": "application/json"},
                json={
                    "inputs": [text[:490]],
                    "target_language_code": SARVAM_LANG_MAP[language],
                    "speaker": "meera",
                    "model": "bulbul:v2",
                },
            )
            if res.status_code == 200:
                audios = res.json().get("audios", [])
                return {"tts_engine_used": "sarvam", "audio_base64": audios[0] if audios else None}
            else:
                print("Sarvam API Error:", res.status_code, res.text)

    # Route 2: English / Clinical Summaries -> Murf TTS
    if not murf_key or "your_" in murf_key:
        return {"tts_engine_used": "murf_mock", "audio_base64": None}

    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(
            "https://api.murf.ai/v1/speech/generate",
            headers={"api-key": murf_key, "Content-Type": "application/json"},
            json={
                "voiceId": "en-IN-priya",
                "text": text,
                "format": "MP3",
                "encodeAsBase64": True,
            },
        )
        if res.status_code == 200:
            return {"tts_engine_used": "murf", "audio_base64": res.json().get("encodedAudio")}

    return {"tts_engine_used": "fallback", "audio_base64": None}