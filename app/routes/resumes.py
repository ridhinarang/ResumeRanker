import os
import uuid
import hashlib
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from app import db
from app.models import Candidate, Resume, Skill, Application, Job
from app.services.resume_parser import (
    extract_text, extract_email, extract_phone, extract_name, extract_experience_years,
    extract_education, extract_projects, extract_certifications, extract_location,
    extract_linkedin, extract_github, extract_graduation_year
)
from app.services.skill_extractor import extract_skills, SKILLS, normalize_skill_list
from app.services.scorer import calculate_score

resumes_bp = Blueprint("resumes", __name__, url_prefix="/resumes")
ALLOWED = {"pdf", "docx"}

@resumes_bp.route("/")
@login_required
def list_resumes():
    search = request.args.get("search", "").strip()
    job_id = request.args.get("job_id", "").strip()
    status = request.args.get("status", "").strip()
    min_score = request.args.get("min_score", "").strip()
    max_score = request.args.get("max_score", "").strip()
    min_exp = request.args.get("min_exp", "").strip()
    skill = request.args.get("skill", "").strip().lower()

    jobs = Job.query.order_by(Job.title.asc()).all()
    candidates = Candidate.query.order_by(Candidate.created_at.desc()).all()
    result = []

    for c in candidates:
        if search and search.lower() not in (c.name or "").lower() and search.lower() not in (c.email or "").lower():
            continue
        apps = c.applications
        if job_id:
            apps = [a for a in apps if str(a.job_id) == job_id]
        if status:
            apps = [a for a in apps if a.status.lower() == status.lower()]
        if min_score:
            try: apps = [a for a in apps if a.match_score >= float(min_score)]
            except ValueError: pass
        if max_score:
            try: apps = [a for a in apps if a.match_score <= float(max_score)]
            except ValueError: pass
        if min_exp:
            try:
                if (c.experience_years or 0) < float(min_exp): continue
            except ValueError: pass
        if skill and not any(skill == s.name.lower() for s in c.skills):
            continue
        if job_id or status or min_score or max_score:
            if not apps:
                continue
        result.append(c)

    return render_template("candidates.html", candidates=result, jobs=jobs, search=search,
                           selected_job=job_id, selected_status=status, min_score=min_score,
                           max_score=max_score, min_exp=min_exp, selected_skill=skill)

@resumes_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        files = [f for f in request.files.getlist("resumes") if f and f.filename]
        if not files:
            flash("Please select at least one resume.", "danger")
            return redirect(request.url)

        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        success = 0
        duplicate = 0
        failed = 0

        for file in files:
            ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
            if ext not in ALLOWED:
                failed += 1
                continue

            data = file.read()
            file.seek(0)
            file_hash = hashlib.sha256(data).hexdigest()
            if Candidate.query.filter_by(resume_hash=file_hash).first():
                duplicate += 1
                continue

            filename = f"{uuid.uuid4().hex}_{file.filename.replace(' ', '_')}"
            path = os.path.join(upload_dir, filename)
            try:
                file.save(path)
                text = extract_text(path)
                if not text.strip():
                    os.remove(path)
                    failed += 1
                    continue

                candidate = Candidate(
                    name=extract_name(text),
                    email=extract_email(text),
                    phone=extract_phone(text),
                    location=extract_location(text),
                    linkedin=extract_linkedin(text),
                    github=extract_github(text),
                    education=extract_education(text),
                    graduation_year=extract_graduation_year(text),
                    experience_years=extract_experience_years(text),
                    projects=extract_projects(text),
                    certifications=extract_certifications(text),
                    resume_hash=file_hash
                )
                db.session.add(candidate)
                db.session.flush()

                for name in extract_skills(text):
                    s = Skill.query.filter_by(name=name).first()
                    if not s:
                        s = Skill(name=name, category=SKILLS[name])
                        db.session.add(s)
                        db.session.flush()
                    candidate.skills.append(s)

                db.session.add(Resume(candidate_id=candidate.id, file_name=file.filename,
                                       file_path=path, raw_text=text))
                db.session.commit()

                for job in Job.query.all():
                    required = normalize_skill_list(job.required_skills)
                    preferred = normalize_skill_list(job.preferred_skills)
                    r = calculate_score(candidate, text, job, [s.name for s in candidate.skills], required, preferred)
                    app = Application.query.filter_by(candidate_id=candidate.id, job_id=job.id).first()
                    if not app:
                        app = Application(candidate_id=candidate.id, job_id=job.id)
                        db.session.add(app)
                    app.match_score = r["match_score"]
                    app.skill_score = r["skill_score"]
                    app.semantic_score = r["semantic_score"]
                    app.experience_score = r["experience_score"]
                    app.education_score = r["education_score"]
                    app.preferred_score = r["preferred_score"]
                    app.certification_score = r["certification_score"]
                    app.matched_skills = ", ".join(r["matched_skills"])
                    app.missing_skills = ", ".join(r["missing_skills"])
                    app.status = "Shortlisted" if r["match_score"] >= 75 else "Review"
                db.session.commit()
                success += 1
            except Exception:
                db.session.rollback()
                if os.path.exists(path):
                    os.remove(path)
                failed += 1

        if success:
            flash(f"{success} resume(s) uploaded and analyzed successfully.", "success")
        if duplicate:
            flash(f"{duplicate} duplicate resume(s) skipped.", "warning")
        if failed:
            flash(f"{failed} file(s) could not be processed.", "danger")
        return redirect(url_for("resumes.list_resumes"))

    return render_template("upload.html")

@resumes_bp.route("/candidate/<int:candidate_id>")
@login_required
def detail(candidate_id):
    candidate = db.session.get(Candidate, candidate_id)
    if not candidate:
        flash("Candidate not found.", "danger")
        return redirect(url_for("resumes.list_resumes"))
    applications = Application.query.filter_by(candidate_id=candidate.id).order_by(Application.match_score.desc()).all()
    return render_template("candidate_detail.html", candidate=candidate, applications=applications)

@resumes_bp.route("/candidate/<int:candidate_id>/status/<int:application_id>", methods=["POST"])
@login_required
def update_status(candidate_id, application_id):
    app_row = db.session.get(Application, application_id)
    if not app_row or app_row.candidate_id != candidate_id:
        flash("Application not found.", "danger")
        return redirect(url_for("resumes.detail", candidate_id=candidate_id))
    app_row.status = request.form.get("status", "Review")
    app_row.recruiter_notes = request.form.get("notes", "")
    db.session.commit()
    flash("Candidate status updated.", "success")
    return redirect(url_for("resumes.detail", candidate_id=candidate_id))

@resumes_bp.route("/candidate/<int:candidate_id>/delete", methods=["POST"])
@login_required
def delete_candidate(candidate_id):
    candidate = db.session.get(Candidate, candidate_id)
    if not candidate:
        flash("Candidate not found.", "danger")
        return redirect(url_for("resumes.list_resumes"))
    for resume in list(candidate.resumes):
        if resume.file_path and os.path.exists(resume.file_path):
            try: os.remove(resume.file_path)
            except OSError: pass
    db.session.delete(candidate)
    db.session.commit()
    flash("Candidate and associated resume data deleted successfully.", "success")
    return redirect(url_for("resumes.list_resumes"))

@resumes_bp.route("/rescore", methods=["POST"])
@login_required
def rescore():
    for job in Job.query.all():
        required = normalize_skill_list(job.required_skills)
        preferred = normalize_skill_list(job.preferred_skills)
        for c in Candidate.query.all():
            resume = c.resumes[-1] if c.resumes else None
            text = resume.raw_text if resume else ""
            r = calculate_score(c, text, job, [s.name for s in c.skills], required, preferred)
            app = Application.query.filter_by(candidate_id=c.id, job_id=job.id).first()
            if not app:
                app = Application(candidate_id=c.id, job_id=job.id)
                db.session.add(app)
            for key in ("match_score","skill_score","semantic_score","experience_score","education_score","preferred_score","certification_score"):
                setattr(app, key, r[key])
            app.matched_skills = ", ".join(r["matched_skills"])
            app.missing_skills = ", ".join(r["missing_skills"])
            if app.status not in {"Interview", "Selected", "Rejected"}:
                app.status = "Shortlisted" if r["match_score"] >= 75 else "Review"
    db.session.commit()
    flash("All candidate matches have been rescored.", "success")
    return redirect(url_for("resumes.list_resumes"))
