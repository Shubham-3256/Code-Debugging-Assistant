# gemini.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

def get_gemini_fix(error_output, code):
    prompt = f"""
You're an expert Python debugger.

A user ran the following code and encountered this error:

--- CODE START ---
{code}
--- CODE END ---

--- ERROR ---
{error_output}
--- ERROR END ---

Please:
1. Explain the error simply
2. Suggest corrections
3. Provide improved code if possible
"""

    try:
        response = model.generate_content(prompt)
        return {
            "explanation": response.text,
            "suggested_fix": response.text  # You can extract cleaned-up code if needed
        }
    except Exception as e:
        return {
            "explanation": f"Error using Gemini: {e}",
            "suggested_fix": ""
        }
