# gemini.py

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

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
Return only explanation and the improved code as plain text.
"""

    try:
        response = model.generate_content(prompt)
        return {
            "explanation": response.text,
            "suggested_fix": response.text  # You can extract or parse if needed
        }
    except Exception as e:
        return {
            "explanation": f"Error using Gemini: {e}",
            "suggested_fix": ""
        }

def analyze_code_quality(code):
    prompt = f"""
You're a strict Python code reviewer.

Analyze the code and return:
1. Score out of 10 (only the number)
2. 2-3 good practices in the code.
3. 2-3 bad practices or areas of improvement.
4. A short summary for improving this code.

--- CODE START ---
{code}
--- CODE END ---

Return your result strictly in this JSON format:

{{
  "score": 7,
  "good_practices": "The code is modular and uses functions. It includes some comments.",
  "bad_practices": "Variable naming could be better. No error handling. No docstrings.",
  "summary": "Overall the code is functional but lacks polish and error handling."
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text

        # Extract and parse the JSON from the response
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        json_str = text[json_start:json_end]
        return json.loads(json_str)

    except Exception as e:
        return {
            "score": 0,
            "good_practices": "N/A",
            "bad_practices": "N/A",
            "summary": f"Error analyzing code quality: {e}"
        }
