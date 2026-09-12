from datetime import datetime
from app import db, _Field, _QueryDescriptor

class _SkillList(list):
    def __init__(self, candidate_id):
        self.candidate_id=candidate_id
        super().__init__(self._load())
    def _load(self):
        with db.connect() as conn:
            rows=conn.execute("""SELECT s.* FROM skill s JOIN candidate_skills cs ON s.id=cs.skill_id
                                 WHERE cs.candidate_id=? ORDER BY s.name""",[self.candidate_id]).fetchall()
        return [Skill._from_row(r) for r in rows]
    def append(self, skill):
        with db.connect() as conn:
            conn.execute("INSERT OR IGNORE INTO candidate_skills(candidate_id,skill_id) VALUES(?,?)",
                         [self.candidate_id,skill.id]); conn.commit()
        if skill not in self: super().append(skill)

class Skill:
    _table="skill"; _fields=["name","category"]
    id=_Field("id"); name=_Field("name"); category=_Field("category"); query=_QueryDescriptor()
    def __init__(self,name="",category="",id=None): self.id=id; self.name=name; self.category=category
    @classmethod
    def _from_row(cls,row): return cls(id=row["id"],name=row["name"],category=row["category"])

class Candidate:
    _table="candidate"
    _fields=["name","email","phone","location","linkedin","github","education","graduation_year",
             "experience_years","experience_text","projects","certifications","resume_hash","created_at"]
    id=_Field("id"); name=_Field("name"); email=_Field("email"); phone=_Field("phone"); location=_Field("location")
    linkedin=_Field("linkedin"); github=_Field("github"); education=_Field("education")
    graduation_year=_Field("graduation_year"); experience_years=_Field("experience_years")
    experience_text=_Field("experience_text"); projects=_Field("projects"); certifications=_Field("certifications")
    resume_hash=_Field("resume_hash"); created_at=_Field("created_at"); query=_QueryDescriptor()
    def __init__(self, id=None, **kwargs):
        self.id=id
        for f in self._fields: setattr(self,f,kwargs.get(f, "" if f!="experience_years" else 0))
        if not self.created_at: self.created_at=datetime.utcnow().isoformat()
    @classmethod
    def _from_row(cls,row):
        return cls(id=row["id"], **{f:row[f] for f in cls._fields})
    @property
    def skills(self): return _SkillList(self.id)
    @property
    def resumes(self):
        from app.models import Resume
        return Resume.query.filter_by(candidate_id=self.id).all()
    @property
    def applications(self):
        from app.models import Application
        return Application.query.filter_by(candidate_id=self.id).all()
