from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Candidate, Job, Application

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def index():
    total_candidates = Candidate.query.count()
    total_jobs = Job.query.count()
    shortlisted = Application.query.filter_by(status="Shortlisted").count()
    interviews = Application.query.filter_by(status="Interview").count()
    selected = Application.query.filter_by(status="Selected").count()
    recent = Candidate.query.order_by(Candidate.created_at.desc()).limit(8).all()
    return render_template(
        "dashboard.html",
        total_candidates=total_candidates,
        total_jobs=total_jobs,
        shortlisted=shortlisted,
        interviews=interviews,
        selected=selected,
        recent=recent
    )
