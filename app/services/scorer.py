from app.services.matcher import semantic_similarity, skill_match, education_match

def calculate_score(candidate, resume_text, job, candidate_skills, required, preferred):
    skill_score, preferred_score, matched, missing = skill_match(
        candidate_skills, required, preferred
    )

    semantic = semantic_similarity(resume_text, job.description)

    if job.min_experience and job.min_experience > 0:
        experience = min(100.0, (candidate.experience_years or 0) / job.min_experience * 100)
    else:
        experience = 100.0

    education = education_match(candidate.education, job.education_requirement)

    cert_req = (job.certification_requirement or "").strip().lower()
    cert_text = (candidate.certifications or "").lower()
    certification = 100.0 if not cert_req else (100.0 if any(
        term.strip() in cert_text for term in cert_req.replace(",", "|").split("|") if term.strip()
    ) else 0.0)

    final = (
        skill_score * 0.35 +
        semantic * 0.20 +
        experience * 0.15 +
        education * 0.10 +
        preferred_score * 0.10 +
        certification * 0.10
    )

    return {
        "match_score": round(final, 2),
        "skill_score": round(skill_score, 2),
        "semantic_score": round(semantic, 2),
        "experience_score": round(experience, 2),
        "education_score": round(education, 2),
        "preferred_score": round(preferred_score, 2),
        "certification_score": round(certification, 2),
        "matched_skills": matched,
        "missing_skills": missing,
    }
