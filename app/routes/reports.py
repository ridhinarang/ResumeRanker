import csv
import io
from flask import Blueprint, Response, render_template, flash, redirect, url_for, abort
from flask_login import login_required
from app.models import Candidate, Application

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/export/csv")
@login_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Candidate","Email","Phone","Job","Match Score","Skill Score",
                     "Semantic Score","Experience Score","Education Score",
                     "Preferred Score","Certification Score","Status"])
    for a in Application.query.order_by(Application.match_score.desc()).all():
        writer.writerow([
            a.candidate.name, a.candidate.email, a.candidate.phone,
            a.job.title, a.match_score, a.skill_score, a.semantic_score,
            a.experience_score, a.education_score, a.preferred_score,
            a.certification_score, a.status
        ])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=candidates.csv"})

@reports_bp.route("/candidate/<int:candidate_id>.pdf")
@login_required
def candidate_pdf(candidate_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    c = Candidate.query.filter_by(id=candidate_id).first()
    if not c:
        abort(404)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [Paragraph("ResumeRank AI - Candidate Evaluation Report", styles["Title"]),
             Spacer(1, 12), Paragraph(f"<b>Candidate:</b> {c.name}", styles["BodyText"]),
             Paragraph(f"<b>Email:</b> {c.email or '—'}", styles["BodyText"]),
             Paragraph(f"<b>Phone:</b> {c.phone or '—'}", styles["BodyText"]),
             Paragraph(f"<b>Experience:</b> {c.experience_years or 0} years", styles["BodyText"]),
             Spacer(1, 12)]
    rows = [["Job", "Match", "Skills", "Semantic", "Experience", "Status"]]
    for a in sorted(c.applications, key=lambda x: x.match_score, reverse=True):
        rows.append([a.job.title, f"{a.match_score:.1f}%", f"{a.skill_score:.1f}%",
                     f"{a.semantic_score:.1f}%", f"{a.experience_score:.1f}%", a.status])
    if len(rows) > 1:
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
                                   ("GRID",(0,0),(-1,-1),0.5,colors.grey),
                                   ("VALIGN",(0,0),(-1,-1),"TOP")]))
        story += [table]
    else:
        story.append(Paragraph("No job matches available.", styles["BodyText"]))
    doc.build(story)
    buf.seek(0)
    return Response(buf.getvalue(), mimetype="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={c.name.replace(' ','_')}_report.pdf"})
