import os
from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

app = FastAPI(title="AI Cyber Cafe Agent Backend")

GENAI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
genai.configure(api_key=GENAI_API_KEY)

class UserTaskRequest(BaseModel):
    user_query: str
    user_data: dict

@app.post("/execute-agent")
def execute_task(request: UserTaskRequest):
    query = request.user_query
    user_info = request.user_data

    # Target URL Resolution
    target_url = "https://sewasetu.assam.gov.in"
    q_lower = query.lower()

    if "basundhara" in q_lower or "land" in q_lower or "mutation" in q_lower:
        target_url = "https://basundhara.assam.gov.in"
    elif "pan" in q_lower:
        target_url = "https://www.onlineservices.nsdl.com"
    elif "aadhaar" in q_lower or "uidai" in q_lower:
        target_url = "https://myaadhaar.uidai.gov.in"

    # Headless Chrome Browser Setup for Render
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(target_url)
        page_title = driver.title

        # Scan text inputs and auto-fill
        inputs = driver.find_elements(By.TAG_NAME, "input")
        filled_count = 0

        for input_field in inputs:
            try:
                field_type = input_field.get_attribute("type") or ""
                if field_type in ["text", "tel"]:
                    name_attr = (input_field.get_attribute("name") or "").lower()
                    placeholder = (input_field.get_attribute("placeholder") or "").lower()

                    if ("name" in name_attr or "name" in placeholder) and "name" in user_info:
                        input_field.send_keys(user_info["name"])
                        filled_count += 1
                    elif ("phone" in name_attr or "mobile" in placeholder) and "phone" in user_info:
                        input_field.send_keys(user_info["phone"])
                        filled_count += 1
            except Exception:
                continue

        driver.quit()

        return {
            "status": "success",
            "page_title": page_title,
            "url": target_url,
            "fields_autofilled": filled_count,
            "message": f"AI Agent mapped '{query}' to {page_title} and auto-filled details."
        }

    except Exception as err:
        return {
            "status": "error",
            "url": target_url,
            "message": f"Browser error: {str(err)}"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
