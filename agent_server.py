import os
import json
import re
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Dynamic AI Agent Backend")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ai_client = genai.Client(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.get("/")
def home():
    return {"status": "online", "message": "Truly Autonomous AI Agent Active"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query

    # Strict AI Prompt expecting JSON response
    prompt = f"""
    You are an AI Web Navigation Agent.
    Find the exact direct official working portal URL for Indian/Assam Govt or private online service for task: '{query}'.
    
    Examples:
    - aadhaar / addhar card -> https://myaadhaar.uidai.gov.in
    - pan card -> https://www.protean-tinpan.com
    - shg / asrlms -> https://asrlms.assam.gov.in
    - sewa setu -> https://sewasetu.assam.gov.in
    - basundhara -> https://basundhara.assam.gov.in
    - seba / hslc -> https://site.sebaonline.org
    
    Output ONLY a valid JSON object. No explanations, no markdown tags.
    {{"url": "https://exact-official-website-url.gov.in", "instruction": "Action guidance"}}
    """

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"  # Enforces pure JSON output from Gemini
            )
        )
        
        clean_text = response.text.strip()
        ai_data = json.loads(clean_text)
        
        target_url = ai_data.get("url", "").strip()
        ai_instruction = ai_data.get("instruction", f"Portal loaded for {query}.")

        # If AI returns empty URL, extract URL using Regex
        if not target_url.startswith("http"):
            urls = re.findall(r'https?://[^\s"]+', response.text)
            target_url = urls[0] if urls else "https://myaadhaar.uidai.gov.in"

    except Exception as e:
        # Emergency intelligent fallback (No Google Search Result redirect)
        q_lower = query.lower()
        if "aadhaar" in q_lower or "addhar" in q_lower or "uidai" in q_lower:
            target_url = "https://myaadhaar.uidai.gov.in"
        elif "pan" in q_lower:
            target_url = "https://www.protean-tinpan.com"
        elif "basundhara" in q_lower or "land" in q_lower:
            target_url = "https://basundhara.assam.gov.in"
        elif "seba" in q_lower:
            target_url = "https://site.sebaonline.org"
        else:
            target_url = "https://sewasetu.assam.gov.in"
            
        ai_instruction = f"Opening official portal for {query}..."

    return {
        "status": "success",
        "url": target_url,
        "message": ai_instruction
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
