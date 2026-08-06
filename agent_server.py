import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Smart AI Cyber Cafe Agent")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ai_client = genai.Client(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.get("/")
def home():
    return {"status": "online", "message": "Smart Reasoning AI Agent Active"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query

    # Real AI System Prompt with Feasibility & Intent Analysis
    prompt = f"""
    You are an expert AI Cyber Cafe Consultant for Indian & Assam State Online Services.
    The user wants to do: '{query}'.

    Carefully analyze:
    1. FEASIBILITY: Can this process be done 100% online, or does it require an offline visit (e.g. Aadhaar New Registration requires biometric visit)?
    2. EXACT ACTIONABLE URL: What is the EXACT direct portal URL (NOT Google search)? E.g. SBI Savings Account -> https://bank.sbi or https://sbionline.sbi, PAN -> https://www.protean-tinpan.com.
    3. GUIDANCE: What documents or steps does the user need?

    RULES:
    - NEVER return a Google Search URL (google.com/search). Always find or infer the direct official portal domain.
    - If the task CANNOT be done online, set "can_execute_online": false and explain clearly in "guidance_message".
    - If it CAN be done online, set "can_execute_online": true, provide the exact direct "url", and list required steps/documents.

    Return ONLY a valid JSON object:
    {{
        "can_execute_online": true,
        "url": "https://bank.sbi",
        "service_title": "SBI Online Account Opening",
        "guidance_message": "1. Keep Aadhaar and PAN Card ready.\\n2. Video KYC will be performed.\\n3. Click proceed to load official portal."
    }}
    """

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        data = json.loads(response.text.strip())
        
        can_online = data.get("can_execute_online", True)
        target_url = data.get("url", "").strip()
        title = data.get("service_title", "Official Portal")
        message = data.get("guidance_message", "Proceeding to official portal...")

        # Guard Against Google Search Links
        if "google.com/search" in target_url or not target_url.startswith("http"):
            target_url = "https://sewasetu.assam.gov.in"

    except Exception as e:
        can_online = True
        target_url = "https://sewasetu.assam.gov.in"
        title = "Official Service Portal"
        message = f"Redirecting to official service portal for {query}."

    return {
        "status": "success",
        "can_execute_online": can_online,
        "url": target_url,
        "service_title": title,
        "message": message
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
