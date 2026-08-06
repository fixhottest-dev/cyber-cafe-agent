import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Dynamic AI Agent Backend")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
ai_client = genai.Client(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.get("/")
def home():
    return {"status": "online", "message": "Truly Autonomous AI Agent is Active!"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query

    # Truly Independent AI Reasoning - No hardcoded URLs
    prompt = f"""
    You are an autonomous AI Navigation Agent for Indian & Assam State online services.
    The user wants to perform this task: '{query}'.
    
    Find or infer the most accurate official working website URL for this task (e.g. for SHG it might be https://nrlm.gov.in or https://asrlms.assam.gov.in).
    If it's an educational board, land service, bank, or welfare scheme, give its direct portal URL.
    
    Return ONLY a valid JSON object in this exact format:
    {{"url": "https://exact-official-website-url.gov.in", "instruction": "Actionable guidance for user in simple Hindi-English"}}
    """

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        # Parse JSON output from Gemini AI
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        ai_data = json.loads(clean_text)
        
        target_url = ai_data.get("url", "https://www.google.com")
        ai_instruction = ai_data.get("instruction", f"Portal for {query} loaded successfully.")

    except Exception as e:
        # Emergency Fallback to direct official Google Search query if AI parsing fails
        target_url = f"https://www.google.com/search?q={query}+official+portal+apply+online"
        ai_instruction = f"Search portal loaded for {query}."

    return {
        "status": "success",
        "url": target_url,
        "message": ai_instruction
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
