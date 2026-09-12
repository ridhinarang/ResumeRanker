from datetime import datetime
from app import db, _Field, _QueryDescriptor

class Application:
    _table="application"
    _fields=["candidate_id","job_id","match_score","skill_score","semantic_score","experience_score",
             "education_score","preferred_score","certification_score","matched_skills","missing_skills",
             "status","recruiter_notes","created_at"]
    id=_Field("id"); candidate_id=_Field("candidate_id"); job_id=_Field("job_id")
    match_score=_Field("match_score"); skill_score=_Field("skill_score"); semantic_score=_Field("semantic_score")
    experience_score=_Field("experience_score"); education_score=_Field("education_score")
    preferred_score=_Field("preferred_score"); certification_score=_Field("certification_score")
    matched_skills=_Field("matched_skills"); missing_skills=_Field("missing_skills")
    status=_Field("status"); recruiter_notes=_Field("recruiter_notes"); created_at=_Field("created_at")
    query=_QueryDescriptor()
    def __init__(self,id=None,**kwargs):
        self.id=id
        defaults={"match_score":0,"skill_score":0,"semantic_score":0,"experience_score":0,"education_score":0,
                  "preferred_score":0,"certification_score":0,"matched_skills":"","missing_skills":"",
                  "status":"Review","recruiter_notes":""}
        for f in self._fields: setattr(self,f,kwargs.get(f,defaults.get(f,"")))
        if not self.created_at: self.created_at=datetime.utcnow().isoformat()
    @classmethod
    def _from_row(cls,row): return cls(id=row["id"],**{f:row[f] for f in cls._fields})
    @property
    def candidate(self):
        from app.models import Candidate
        return db.session.get(Candidate,self.candidate_id)
    @property
    def job(self):
        from app.models import Job
        return db.session.get(Job,self.job_id)
