import fitz  
import docx  
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def extract_text_from_pdf(file_path):
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text("text")
    except Exception as e:
        print("PDF extraction error:", e)
    return text


def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print("DOCX extraction error:", e)
    return text


def extract_text(file_path):
    file_ext = file_path.lower()

    if file_ext.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_ext.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX allowed.")


def parse_resume_with_ai(text):
    prompt = f"""
    Extract structured information from this resume.

    Resume Text:
    {text}

    Return a JSON with fields strictly in the following format:
    {{
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "education": [],
        "experience_years": 0,
        "projects": [],
        "raw_text": ""
    }}

    - skills must be a list of strings
    - education must be a list of strings
    - projects must be a list of short strings
    - experience_years must be a number
    - raw_text must contain the full resume text
    """

    model = genai.GenerativeModel("gemini-pro")

    try:
        response = model.generate_content(prompt)
        parsed = json.loads(response.text)

        parsed["raw_text"] = text
        return parsed

    except Exception as e:
        print("LLM Parsing Error:", e)
        return {
            "raw_text": text,
            "skills": [],
            "education": [],
            "projects": [],
            "experience_years": 0
        }


def parse_resume(file_path):
    text = extract_text(file_path)
    if len(text.strip()) == 0:
        return {"error": "Could not extract text from file."}

    parsed_json = parse_resume_with_ai(text)

    parsed_json["raw_text"] = text

    return parsed_json
