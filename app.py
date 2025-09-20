# backend/main.py
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from src.schemas.schemas import Query
from src.agents.call_agent import CallAgent
from src.memory.database import init_db, book_complaint, get_complaint_status, get_customer_history
from dotenv import load_dotenv
import pyttsx3
import os
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY") 
app = FastAPI()

llm = CallAgent(key=groq_api_key)

init_db()

@app.get("/", tags=["authentication"])
def index():
    return RedirectResponse(url="/docs")

@app.post("/chat")
def chat(query: Query):
    parsed = llm.call(query.user_input)
    print(f"Parsed: {parsed}")
    intent = parsed["intent"]
    name = parsed["customer_name"]
    cid = parsed["complaint_id"]
    desc = parsed["description"]

    if intent == "book_complaint":
        if not name or not desc:
            return {"response": "Missing details: name/description"}
        response = book_complaint(name, desc)
    elif intent == "check_status":
        if not cid:
            return {"response": "Missing complaint ID"}
        response = get_complaint_status(cid)
    elif intent == "customer_history":
        if not name:
            return {"response": "Missing customer name"}
        response = get_customer_history(name)
    else:
        response = "Sorry, I couldn't understand your request."

    return {"response": response}
