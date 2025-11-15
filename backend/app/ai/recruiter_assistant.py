import json, os
from dotenv import load_dotenv
import google.generativeai as genai
from ..database.candidate import CandidateDB

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def answer_recruiter_query(query_text, recruiter_context=None, top_candidates=5):
    candidates = CandidateDB.get_top_n(recruiter_context.get("job_role_id"), n=top_candidates) if recruiter_context else []
    prompt = f"""
You are RecruiterAssistant. Query: {query_text}
Context candidates: {json.dumps(candidates)}
Provide concise answer and list top candidate IDs if asked.
Return JSON.
"""
    model = genai.GenerativeModel("gemini-pro")
    resp = model.generate_content(prompt)
    try:
        return json.loads(resp.text)
    except Exception:
        return {"raw": resp.text}
