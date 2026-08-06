import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AI Cyber Cafe Agent Backend")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ai_client = genai.Client(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.get("/")
def home():
    return {"status": "online", "message": "Backend Server Ready"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query
    q = query.lower()

    # Direct Dynamic Intent Mapping Matrix
    target_url = ""
    is_ready = True
    message = "Opening requested portal..."

    if "pan" in q:
        target_url = "https://www.protean-tinpan.com"
        message = "Opening PAN Card application portal..."
    elif "aadhaar" in q or "addhar" in q or "uidai" in q:
        target_url = "https://myaadhaar.uidai.gov.in"
        message = "Opening official myAadhaar portal..."
    elif "seba" in q or "hslc" in q or "admit" in q:
        target_url = "https://site.sebaonline.org"
        message = "Opening SEBA Assam portal..."
    elif "basundhara" in q or "land" in q or "mutation" in q or "jamabandi" in q:
        target_url = "https://basundhara.assam.gov.in"
        message = "Opening Mission Basundhara portal..."
    elif "shg" in q or "asrlms" in q or "nrlm" in q:
        target_url = "https://asrlms.assam.gov.in"
        message = "Opening Assam State Rural Livelihoods Mission portal..."
    elif "income" in q or "prc" in q or "caste" in q or "sewa" in q:
        target_url = "https://sewasetu.assam.gov.in"
        message = "Opening Sewa Setu Assam portal..."
    elif "voter" in q or "epic" in q:
        target_url = "https://voters.eci.gov.in"
        message = "Opening Voter Services portal..."
    elif "pf" in q or "epf" in q or "uan" in q:
        target_url = "https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
        message = "Opening EPFO Member portal..."
    else:
        # Fallback using Gemini Model 1.5 Flash
        try:
            prompt = f"Give the direct official website URL for Indian service: '{query}'. Output ONLY valid JSON: {{\"url\": \"https://...\", \"message\": \"Success\"}}"
            response = ai_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)
            target_url = data.get("url", "https://sewasetu.assam.gov.in")
            message = "Opening official website..."
        except Exception as e:
            target_url = f"https://www.google.com/search?q={query}+official+website"
            message = f"Searching official portal for {query}..."

    return {
        "status": "success",
        "is_ready": is_ready,
        "url": target_url,
        "message": message
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
