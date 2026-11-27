import os
import json
import httpx

SYSTEM_PROMPT = """
You are Jynex, a warm, empathetic multilingual healthcare voice companion for Indian patients.
Rules:
1. Reply in the EXACT same language/script the patient uses (Hindi, Gujarati, Marathi, Hinglish, Gujlish, or Indian English).
2. Keep spoken replies short (2-3 simple sentences max) so TTS sounds natural.
3. For symptom intake, ask ONLY ONE follow-up question at a time (e.g., duration, severity, fever, existing medication/allergies). Never prescribe prescription-only drugs; suggest safe hydration/rest and doctor consultation.
4. Always return valid JSON ONLY with keys:
   - "reply_text": string (spoken response in patient's language)
   - "language": one of ["hi", "gu", "mr", "en"]
   - "medicine_cards": list of objects [{"name": "", "timing": "Morning/Night", "food": "After meal", "note_local": ""}] (empty list if not discussing a prescription)
   - "doctor_summary": object or null ({"chief_complaint": "", "duration": "", "severity": "", "associated_symptoms": [], "recommended_next_step": ""} once 3+ details are gathered, else null)
"""

async def generate_medical_response(user_text: str, history: list[dict]) -> dict:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or "your_" in api_key:
        return {
            "reply_text": "Namaste! Main Jynex hoon. Aapko yeh takleef kab se ho rahi hai?",
            "language": "hi",
            "medicine_cards": [],
            "doctor_summary": None,
        }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history[-6:] + [
        {"role": "user", "content": user_text}
    ]

    async with httpx.AsyncClient(timeout=20.0) as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
        )
        if res.status_code != 200:
            print("Groq API Error:", res.status_code, res.text)
            res.raise_for_status()
        content = res.json()["choices"][0]["message"]["content"]
        return json.loads(content)