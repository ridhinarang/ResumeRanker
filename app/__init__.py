import os
import sqlite3
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "resume_ranker.db")


class _Field:
    def __init__(self, name):
        self.name = name
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    def __set__(self, instance, value):
        instance.__dict__[self.name] = value
        session = globals().get("db")
        if session is not None and getattr(instance, "id", None) is not None:
            try: db.session.dirty.add(instance)
            except AttributeError: pass
    def desc(self):
        return ("DESC", self.name)
    def asc(self):
        return ("ASC", self.name)


class _Query:
    def __init__(self, model, filters=None, order=None, limit_value=None):
        self.model = model
        self.filters = filters or []
        self.order = order
        self.limit_value = limit_value

    def filter_by(self, **kwargs):
        return _Query(self.model, self.filters + list(kwargs.items()), self.order, self.limit_value)

    def order_by(self, field):
        direction, name = field if isinstance(field, tuple) else ("ASC", field.name)
        return _Query(self.model, self.filters, (direction, name), self.limit_value)

    def limit(self, n):
        return _Query(self.model, self.filters, self.order, n)

    def all(self):
        return _fetch_all(self.model, self.filters, self.order, self.limit_value)

    def first(self):
        rows = self.limit(1).all()
        return rows[0] if rows else None

    def count(self):
        where, params = _where(self.filters)
        sql = f"SELECT COUNT(*) FROM {self.model._table}{where}"
        with db.connect() as conn:
            return int(conn.execute(sql, params).fetchone()[0])


class _QueryDescriptor:
    def __get__(self, instance, owner):
        return _Query(owner)


class _Session:
    def __init__(self):
        self.pending = []
        self.dirty = set()

    def add(self, obj):
        if obj not in self.pending and getattr(obj, "id", None) is None:
            self.pending.append(obj)
        elif obj not in self.pending:
            self.pending.append(obj)

    def _write_pending(self):
        db._write_pending()

    def flush(self):
        db._write_pending()

    def commit(self):
        db._write_pending()

    def rollback(self):
        self.pending.clear()
        self.dirty.clear()

    def get(self, model, object_id):
        return _Query(model).filter_by(id=object_id).first()

    def delete(self, obj):
        _delete_object(obj)


class _DB:
    session = _Session()

    def connect(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_all(self):
        with self.connect() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS candidate (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                location TEXT,
                linkedin TEXT,
                github TEXT,
                education TEXT,
                graduation_year INTEGER,
                experience_years REAL DEFAULT 0,
                experience_text TEXT,
                projects TEXT,
                certifications TEXT,
                resume_hash TEXT UNIQUE,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS skill (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT
            );
            CREATE TABLE IF NOT EXISTS candidate_skills (
                candidate_id INTEGER NOT NULL,
                skill_id INTEGER NOT NULL,
                PRIMARY KEY (candidate_id, skill_id),
                FOREIGN KEY(candidate_id) REFERENCES candidate(id) ON DELETE CASCADE,
                FOREIGN KEY(skill_id) REFERENCES skill(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS resume (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                raw_text TEXT,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY(candidate_id) REFERENCES candidate(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS job (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT DEFAULT '',
                preferred_skills TEXT DEFAULT '',
                min_experience REAL DEFAULT 0,
                education_requirement TEXT DEFAULT '',
                certification_requirement TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS application (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                match_score REAL DEFAULT 0,
                skill_score REAL DEFAULT 0,
                semantic_score REAL DEFAULT 0,
                experience_score REAL DEFAULT 0,
                education_score REAL DEFAULT 0,
                preferred_score REAL DEFAULT 0,
                certification_score REAL DEFAULT 0,
                matched_skills TEXT DEFAULT '',
                missing_skills TEXT DEFAULT '',
                status TEXT DEFAULT 'Review',
                recruiter_notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                UNIQUE(candidate_id, job_id),
                FOREIGN KEY(candidate_id) REFERENCES candidate(id) ON DELETE CASCADE,
                FOREIGN KEY(job_id) REFERENCES job(id) ON DELETE CASCADE
            );
            """)
            conn.commit()

    def _write_pending(self):
        if not self.session.pending and not self.session.dirty:
            return
        from app.models import User, Candidate, Skill, Resume, Job, Application
        objs = list(self.session.pending)
        self.session.pending.clear()
        dirty = list(self.session.dirty)
        self.session.dirty.clear()

        with self.connect() as conn:
            for obj in objs + dirty:
                table = obj._table
                fields = obj._fields
                values = [getattr(obj, f, None) for f in fields]
                if getattr(obj, "id", None) is None:
                    placeholders = ",".join("?" for _ in fields)
                    cur = conn.execute(
                        f"INSERT INTO {table} ({','.join(fields)}) VALUES ({placeholders})", values
                    )
                    obj.id = cur.lastrowid
                else:
                    assignments = ",".join(f"{f}=?" for f in fields)
                    conn.execute(
                        f"UPDATE {table} SET {assignments} WHERE id=?", values + [obj.id]
                    )
            conn.commit()


db = _DB()


def _where(filters):
    if not filters:
        return "", []
    clauses, params = [], []
    for key, value in filters:
        clauses.append(f"{key} = ?")
        params.append(value)
    return " WHERE " + " AND ".join(clauses), params


def _fetch_all(model, filters, order, limit_value):
    where, params = _where(filters)
    sql = f"SELECT * FROM {model._table}{where}"
    if order:
        direction, name = order
        sql += f" ORDER BY {name} {direction}"
    if limit_value is not None:
        sql += f" LIMIT {int(limit_value)}"
    with db.connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [model._from_row(row) for row in rows]


def _delete_object(obj):
    table = obj._table
    with db.connect() as conn:
        conn.execute(f"DELETE FROM {table} WHERE id=?", [obj.id])
        conn.commit()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.resumes import resumes_bp
    from app.routes.jobs import jobs_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(reports_bp)

    with app.app_context():
        db.create_all()

    return app
