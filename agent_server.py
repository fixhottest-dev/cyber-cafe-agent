import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Cyber Cafe AI Agent Backend")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ai_client = genai.Client(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.get("/")
def home():
    return {"status": "online", "message": "Cyber Cafe AI Agent Live!"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query
    q_lower = query.lower()

    # 1. Hardcoded High-Precision Direct Routing (Bypasses Google Search)
    target_url = ""
    
    if "pan" in q_lower:
        target_url = "https://www.protean-tinpan.com"
    elif "seba" in q_lower or "hslc" in q_lower or "admit card" in q_lower:
        target_url = "https://site.sebaonline.org"
    elif "sewa" in q_lower or "income" in q_lower or "prc" in q_lower or "caste" in q_lower:
        target_url = "https://sewasetu.assam.gov.in"
    elif "basundhara" in q_lower or "land" in q_lower or "mutation" in q_lower or "jamabandi" in q_lower:
        target_url = "https://basundhara.assam.gov.in"
    elif "aadhaar" in q_lower or "uidai" in q_lower:
        target_url = "https://myaadhaar.uidai.gov.in"
    elif "pf" in q_lower or "epf" in q_lower or "uan" in q_lower:
        target_url = "https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
    elif "voter" in q_lower or "epic" in q_lower:
        target_url = "https://voters.eci.gov.in"
    elif "passport" in q_lower:
        target_url = "https://www.passportindia.gov.in"
    elif "driving" in q_lower or "parivahan" in q_lower or "dl" in q_lower:
        target_url = "https://parivahan.gov.in"
    else:
        # Fallback to direct SEBA / Sewa Setu official portal instead of Google
        target_url = "https://sewasetu.assam.gov.in"

    # 2. AI Guidance Prompt
    prompt = f"Provide 2 short action steps in Hindi-English for user applying/accessing '{query}' on official website."
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        ai_instruction = response.text
    except Exception:
        ai_instruction = "Official Portal loaded. Proceed with online form registration."

    return {
        "status": "success",
        "url": target_url,
        "message": ai_instruction
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
