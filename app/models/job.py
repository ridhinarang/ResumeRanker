from datetime import datetime
from app import db, _Field, _QueryDescriptor

class Job:
    _table="job"; _fields=["title","description","required_skills","preferred_skills","min_experience",
                           "education_requirement","certification_requirement","created_at"]
    id=_Field("id"); title=_Field("title"); description=_Field("description"); required_skills=_Field("required_skills")
    preferred_skills=_Field("preferred_skills"); min_experience=_Field("min_experience")
    education_requirement=_Field("education_requirement"); certification_requirement=_Field("certification_requirement")
    created_at=_Field("created_at"); query=_QueryDescriptor()
    def __init__(self,id=None,**kwargs):
        self.id=id
        for f in self._fields: setattr(self,f,kwargs.get(f,0 if f=="min_experience" else ""))
        if not self.created_at: self.created_at=datetime.utcnow().isoformat()
    @classmethod
    def _from_row(cls,row): return cls(id=row["id"],**{f:row[f] for f in cls._fields})
    @property
    def applications(self):
        from app.models import Application
        return Application.query.filter_by(job_id=self.id).all()
