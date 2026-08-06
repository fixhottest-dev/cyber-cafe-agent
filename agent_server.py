import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
import google.generativeai as genai

app = FastAPI(title="AI Cyber Cafe Agent Backend")

# Set your Gemini API Key in Environment or hardcode here
GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str      # E.g., "Assam me income certificate apply karna hai"
    user_data: dict      # E.g., {"name": "Dilwar Hussain", "phone": "9876543210"}

@app.post("/execute-agent")
async def execute_task(request: UserTaskRequest):
    query = request.user_query
    user_info = request.user_data

    # --- PHASE 1: AI Brain Intent & URL Resolver ---
    target_url = "https://sewasetu.assam.gov.in"
    q_lower = query.lower()

    if "basundhara" in q_lower or "land" in q_lower or "mutation" in q_lower:
        target_url = "https://basundhara.assam.gov.in"
    elif "pan" in q_lower:
        target_url = "https://www.onlineservices.nsdl.com"
    elif "aadhaar" in q_lower or "uidai" in q_lower:
        target_url = "https://myaadhaar.uidai.gov.in"
    elif "income" in q_lower or "caste" in q_lower or "prc" in q_lower or "sewa setu" in q_lower:
        target_url = "https://sewasetu.assam.gov.in"

    # --- PHASE 2: Cloud Playwright Automation ---
    async with async_playwright() as p:
        # Development me headless=False karke live browser dekh sakte ho
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(target_url, timeout=60000)
            page_title = await page.title()

            # Input fields scan & Auto-fill
            inputs = await page.query_selector_all("input[type='text'], input[type='tel']")
            filled_count = 0

            for input_field in inputs:
                name_attr = (await input_field.get_attribute("name") or "").lower()
                placeholder = (await input_field.get_attribute("placeholder") or "").lower()

                if ("name" in name_attr or "name" in placeholder) and "name" in user_info:
                    await input_field.fill(user_info["name"])
                    filled_count += 1
                elif ("phone" in name_attr or "mobile" in placeholder) and "phone" in user_info:
                    await input_field.fill(user_info["phone"])
                    filled_count += 1

            await browser.close()

            return {
                "status": "success",
                "page_title": page_title,
                "url": target_url,
                "fields_autofilled": filled_count,
                "message": f"AI Agent mapped '{query}' to {page_title} and auto-filled details."
            }

        except Exception as err:
            await browser.close()
            return {
                "status": "error",
                "url": target_url,
                "message": f"Execution error: {str(err)}"
            }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
