import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise Exception("❌ GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=api_key)

# ✅ Use just "gemini-pro" instead of "models/gemini-pro"
model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(question, trip_summary):
    prompt = (
        "You are a CO₂ emissions expert for logistics. "
        "Explain TTW, WTT, WTW and suggest how to reduce emissions.\n\n"
        f"Trip Info:\n{trip_summary}\n\n"
        f"Question: {question}"
    )
    response = model.generate_content(prompt)
    return response.text

