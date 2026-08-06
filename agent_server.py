import os
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

class UserTaskRequest(BaseModel):
    user_query: str

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query
    q = query.lower()

    # Smart Reasoning Logic
    if "pan" in q:
        return {
            "can_execute_online": True,
            "url": "https://www.protean-tinpan.com",
            "service_title": "PAN Card Portal",
            "message": "1. Keep Aadhaar and Photo ready.\n2. Proceed to apply online via e-KYC."
        }
    elif "addhar" in q or "aadhaar" in q:
        is_new = "new" in q or "naya" in q
        return {
            "can_execute_online": not is_new,
            "url": "https://myaadhaar.uidai.gov.in" if not is_new else "",
            "service_title": "Aadhaar Services",
            "message": "Naya Aadhaar enrollment online nahi banta, nearest Aadhaar Seva Kendra jana padega." if is_new else "1. Keep registered mobile ready for OTP.\n2. Proceed to myAadhaar portal."
        }
    elif "basundhara" in q or "land" in q:
        return {
            "can_execute_online": True,
            "url": "https://basundhara.assam.gov.in",
            "service_title": "Mission Basundhara",
            "message": "Land record and mutation services portal loaded."
        }
    else:
        return {
            "can_execute_online": True,
            "url": "https://sewasetu.assam.gov.in",
            "service_title": "Sewa Setu Assam",
            "message": "Opening official Sewa Setu portal for Assam government services."
        }
