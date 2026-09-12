from datetime import datetime
from app import db, _Field, _QueryDescriptor

class Resume:
    _table="resume"; _fields=["candidate_id","file_name","file_path","raw_text","uploaded_at"]
    id=_Field("id"); candidate_id=_Field("candidate_id"); file_name=_Field("file_name"); file_path=_Field("file_path")
    raw_text=_Field("raw_text"); uploaded_at=_Field("uploaded_at"); query=_QueryDescriptor()
    def __init__(self,id=None,**kwargs):
        self.id=id
        for f in self._fields: setattr(self,f,kwargs.get(f,""))
        if not self.uploaded_at: self.uploaded_at=datetime.utcnow().isoformat()
    @classmethod
    def _from_row(cls,row): return cls(id=row["id"],**{f:row[f] for f in cls._fields})
    @property
    def candidate(self):
        from app.models import Candidate
        return db.session.get(Candidate,self.candidate_id)
