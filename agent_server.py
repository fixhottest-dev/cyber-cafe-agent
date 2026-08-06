import os
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
    return {"status": "online", "message": "AI Cyber Cafe Backend Server is Running!"}

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query
    q_lower = query.lower()

    # Smart Official URL Routing Matrix
    target_url = ""
    
    if "sewa" in q_lower or "income" in q_lower or "prc" in q_lower or "caste" in q_lower:
        target_url = "https://sewasetu.assam.gov.in"
    elif "basundhara" in q_lower or "land" in q_lower or "mutation" in q_lower or "jamabandi" in q_lower:
        target_url = "https://basundhara.assam.gov.in"
    elif "pan" in q_lower:
        target_url = "https://www.onlineservices.nsdl.com/paam/endUserRegisterContact.html"
    elif "aadhaar" in q_lower or "uidai" in q_lower:
        target_url = "https://myaadhaar.uidai.gov.in"
    elif "pf" in q_lower or "epf" in q_lower:
        target_url = "https://unifiedportal-mem.epfindia.gov.in/memberinterface/"
    else:
        # Fallback to direct Google Search query if portal is unknown
        target_url = f"https://www.google.com/search?q={query}+official+website+apply+online"

    # Use Gemini AI to generate action instructions for user
    prompt = f"User wants to do: '{query}'. Give 2-3 short, clear bullet steps in simple Hindi-English on how to proceed on the website."
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        ai_instruction = response.text
    except Exception:
        ai_instruction = "Website load ho rahi hai. Kripya portal par diye gaye instructions ko follow karein."

    return {
        "status": "success",
        "url": target_url,
        "message": ai_instruction
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
