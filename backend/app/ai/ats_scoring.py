import re
from collections import Counter

ACTION_VERBS = set([
    "achieved","built","designed","developed","implemented","led","managed","created",
    "reduced","improved","optimized","deployed","automated","analyzed"
])

SECTION_HEADERS = ["experience", "education", "skills", "projects", "certifications", "summary", "contact"]

def normalize(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())

def count_action_verbs(text):
    tokens = re.findall(r'\w+', text.lower())
    return sum(1 for t in tokens if t in ACTION_VERBS)

def detect_sections(text):
    """
    Returns set of found common sections.
    Looks for header words followed by newline or colon.
    """
    found = set()
    for h in SECTION_HEADERS:
        if re.search(rf'\b{h}\b\s*[:\n]', text, flags=re.IGNORECASE):
            found.add(h)
    return found

def keyword_coverage(text, keywords, synonyms_map=None):
    """
    Count presence of keywords or their synonyms in text.
    synonyms_map: dict {"skill": ["alt1","alt2"]}
    """
    text_norm = normalize(text)
    count = 0
    for k in keywords:
        k_norm = k.lower()
        if k_norm in text_norm:
            count += 1
        elif synonyms_map and k_norm in synonyms_map:
            alts = synonyms_map[k_norm]
            if any(alt in text_norm for alt in alts):
                count += 1
    return count / max(len(keywords), 1)

def compute_ats_score(resume_text, jd_required_skills, synonyms_map=None):
    """
    Components:
      - section_score (30%): presence of common sections
      - action_verb_score (20%): presence of action verbs in experience bullets
      - keyword_score (40%): coverage of required skills (with synonyms)
      - length_score (10%): reasonable length (100-900 words)
    Returns 0-100.
    """
    t = normalize(resume_text)
    words = re.findall(r'\w+', t)
    wc = len(words)

    sections = detect_sections(resume_text)
    section_score = min(1.0, len(sections) / 3.0)  

    av_count = count_action_verbs(resume_text)
    action_score = min(1.0, av_count / 4.0)  

    keyword_score = keyword_coverage(resume_text, jd_required_skills, synonyms_map)  

    if wc < 80:
        length_score = wc / 80.0  
    elif wc > 1200:
        length_score = 0.8  
    else:
        length_score = 1.0

    final = (section_score * 0.3) + (action_score * 0.2) + (keyword_score * 0.4) + (length_score * 0.1)
    return round(final * 100, 2)
