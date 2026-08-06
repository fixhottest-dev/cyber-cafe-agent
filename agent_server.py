import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Conversational AI Agent Backend")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ai_client = genai.Client(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.get("/")
def home():
    return {"status": "online", "message": "Conversational AI Agent Active"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query

    # Conversational Agent Prompt - Expecting intake reasoning or final action
    prompt = f"""
    You are an expert Autonomous Cyber Cafe AI Assistant. 
    The user wants help with: '{query}'.
    
    Analyze the user's intent carefully:
    1. If the user's input is too vague, incomplete, or missing specific details (e.g., just "aadhaar card", "pan card", "loan"), DO NOT send them to a website yet. Instead, ask them 1-2 clarifying questions to gather their exact requirement and details (like name, purpose, mobile number).
    2. If the user's input has clear intent and details, provide the exact direct official working portal URL and actionable steps.
    
    Return ONLY a valid JSON object in this exact format:
    {{
      "is_ready": false, 
      "url": "", 
      "message": "Aap Aadhaar card me kya karna chahte hain? Naya banwana hai ya address update karna hai? Kripya detail dein."
    }}
    OR if ready:
    {{
      "is_ready": true, 
      "url": "https://myaadhaar.uidai.gov.in", 
      "message": "Aadhaar official portal loaded. Kripya apna Aadhaar number aur OTP enter karein."
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
        
        ai_data = json.loads(response.text.strip())
        is_ready = ai_data.get("is_ready", False)
        target_url = ai_data.get("url", "")
        message = ai_data.get("message", "Kripya apne kaam ki poori detail dein.")

    except Exception as e:
        is_ready = False
        target_url = ""
        message = f"Maine aapka sawaal '{query}' suna. Kripya thoda aur detail me batayein ki aapko exactly kya karwana hai?"

    return {
        "status": "success",
        "is_ready": is_ready,
        "url": target_url,
        "message": message
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
