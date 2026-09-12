from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.models import Job, Candidate, Application
from app.services.skill_extractor import normalize_skill_list
from app.services.scorer import calculate_score


jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.route("/")
@login_required
def list_jobs():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template("jobs.html", jobs=jobs)


@jobs_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_job():

    if request.method == "POST":

        job = Job(
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip(),
            required_skills=request.form.get("required_skills", "").strip(),
            preferred_skills=request.form.get("preferred_skills", "").strip(),
            min_experience=float(request.form.get("min_experience") or 0),
            education_requirement=request.form.get(
                "education_requirement", ""
            ).strip(),
            certification_requirement=request.form.get(
                "certification_requirement", ""
            ).strip()
        )

        if not job.title or not job.description:
            flash("Job title and description are required.", "danger")
            return redirect(request.url)

        db.session.add(job)
        db.session.commit()

        # Score all existing candidates for the new job
        _score_all(job, reset_status=True)

        flash("Job created and candidates scored.", "success")

        return redirect(
            url_for("jobs.detail", job_id=job.id)
        )

    return render_template(
        "job_form.html",
        job=None,
        editing=False
    )


@jobs_bp.route("/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):

    job = db.session.get(Job, job_id)

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    # -----------------------------
    # SAVE EDITED JOB
    # -----------------------------
    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not description:
            flash(
                "Job title and description are required.",
                "danger"
            )

            return render_template(
                "job_form.html",
                job=job,
                editing=True
            )

        try:
            min_experience = float(
                request.form.get("min_experience") or 0
            )
        except ValueError:

            flash(
                "Minimum experience must be a valid number.",
                "danger"
            )

            return render_template(
                "job_form.html",
                job=job,
                editing=True
            )

        # Update JD fields
        job.title = title
        job.description = description

        job.required_skills = request.form.get(
            "required_skills", ""
        ).strip()

        job.preferred_skills = request.form.get(
            "preferred_skills", ""
        ).strip()

        job.min_experience = min_experience

        job.education_requirement = request.form.get(
            "education_requirement", ""
        ).strip()

        job.certification_requirement = request.form.get(
            "certification_requirement", ""
        ).strip()

        db.session.commit()

        # Recalculate rankings using the updated JD.
        # Existing candidate statuses are preserved.
        _score_all(
            job,
            reset_status=False
        )

        flash(
            "Job updated and candidate rankings recalculated.",
            "success"
        )

        return redirect(
            url_for("jobs.detail", job_id=job.id)
        )

    # -----------------------------
    # SHOW EDIT FORM
    # -----------------------------
    return render_template(
        "job_form.html",
        job=job,
        editing=True
    )


@jobs_bp.route("/<int:job_id>")
@login_required
def detail(job_id):

    job = db.session.get(Job, job_id)

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    applications = (
        Application.query
        .filter_by(job_id=job.id)
        .order_by(Application.match_score.desc())
        .all()
    )

    return render_template(
        "job_detail.html",
        job=job,
        applications=applications
    )


@jobs_bp.route("/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):

    job = db.session.get(Job, job_id)

    if not job:
        flash("Job not found.", "danger")
        return redirect(url_for("jobs.list_jobs"))

    db.session.delete(job)
    db.session.commit()

    flash("Job deleted.", "success")

    return redirect(
        url_for("jobs.list_jobs")
    )


def _score_all(job, reset_status=True):

    required = normalize_skill_list(
        job.required_skills
    )

    preferred = normalize_skill_list(
        job.preferred_skills
    )

    candidates = Candidate.query.all()

    for candidate in candidates:

        # Use latest resume
        resume = (
            candidate.resumes[-1]
            if candidate.resumes
            else None
        )

        text = (
            resume.raw_text
            if resume
            else ""
        )

        result = calculate_score(
            candidate,
            text,
            job,
            [s.name for s in candidate.skills],
            required,
            preferred
        )

        application = (
            Application.query
            .filter_by(
                candidate_id=candidate.id,
                job_id=job.id
            )
            .first()
        )

        if not application:

            application = Application(
                candidate_id=candidate.id,
                job_id=job.id
            )

            db.session.add(application)

        # Update scores
        application.match_score = result["match_score"]
        application.skill_score = result["skill_score"]
        application.semantic_score = result["semantic_score"]
        application.experience_score = result["experience_score"]
        application.education_score = result["education_score"]
        application.preferred_score = result["preferred_score"]
        application.certification_score = result[
            "certification_score"
        ]

        # Update skill information
        application.matched_skills = ", ".join(
            result["matched_skills"]
        )

        application.missing_skills = ", ".join(
            result["missing_skills"]
        )

        # Only automatically assign status when creating
        # a new job. Do NOT overwrite recruiter decisions
        # when editing an existing JD.
        if reset_status:
            if result["match_score"] >= 75:
                application.status = "Shortlisted"
            else:
                application.status = "Review"

    db.session.commit()