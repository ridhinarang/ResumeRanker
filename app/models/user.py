from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager, _Field

class User(UserMixin):
    _table = "user"
    _fields = ["name", "email", "password_hash"]
    id = _Field("id")
    name = _Field("name"); email = _Field("email"); password_hash = _Field("password_hash")
    query = __import__("app")._QueryDescriptor()

    def __init__(self, name="", email="", password_hash="", id=None):
        self.id=id; self.name=name; self.email=email; self.password_hash=password_hash
    @classmethod
    def _from_row(cls,row):
        return cls(id=row["id"], name=row["name"], email=row["email"], password_hash=row["password_hash"])
    def set_password(self,password): self.password_hash=generate_password_hash(password)
    def check_password(self,password): return check_password_hash(self.password_hash,password)

@login_manager.user_loader
def load_user(user_id):
    try: return db.session.get(User, int(user_id))
    except (TypeError, ValueError): return None
