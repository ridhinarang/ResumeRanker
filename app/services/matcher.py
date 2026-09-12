import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def semantic_similarity(resume_text, job_text):
    resume_text = resume_text or ""
    job_text = job_text or ""
    if not resume_text.strip() or not job_text.strip():
        return 0.0
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(
            [resume_text, job_text]
        )
        score = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0]) * 100
        return max(0.0, min(100.0, score))
    except Exception:
        return 0.0

def skill_match(candidate_skills, required, preferred):
    c = {x.lower() for x in candidate_skills}
    req = {x.lower() for x in required}
    pref = {x.lower() for x in preferred}
    matched_req = sorted(c & req)
    missing_req = sorted(req - c)
    matched_pref = sorted(c & pref)
    req_score = 100.0 if not req else len(matched_req) / len(req) * 100
    pref_score = 100.0 if not pref else len(matched_pref) / len(pref) * 100
    return req_score, pref_score, matched_req, missing_req

def education_match(candidate_education, requirement):
    if not requirement:
        return 100.0
    text = (candidate_education or "").lower()
    terms = [x.strip().lower() for x in re.split(r"[,/|]+", requirement) if x.strip()]
    return 100.0 if any(term in text for term in terms) else 0.0
