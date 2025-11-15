import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_feedback(candidate, job_role):
    prompt = f"""
    Provide resume feedback for a candidate applying to this job.

    Candidate:
    {json.dumps(candidate)}

    Job Role:
    {json.dumps(job_role)}

    Give:
    - strengths
    - weaknesses
    - skill improvements
    - summary (2-3 sentences)
    Return in JSON.
    """

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return json.loads(response.text)
