import re


# ============================================================
# SKILL CATALOG
# ============================================================

SKILL_CATALOG = [
    # Programming Languages
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "C#",
    "Go",
    "Rust",
    "PHP",
    "Ruby",
    "Kotlin",
    "Swift",
    "Dart",
    "R",
    "MATLAB",
    "Scala",
    "Perl",

    # Web Development
    "HTML",
    "CSS",
    "Bootstrap",
    "Tailwind CSS",
    "React",
    "Angular",
    "Vue.js",
    "Node.js",
    "Express.js",
    "Next.js",
    "Django",
    "Flask",
    "FastAPI",
    "Spring",
    "Spring Boot",
    "ASP.NET",
    "jQuery",

    # Databases
    "SQL",
    "MySQL",
    "PostgreSQL",
    "SQLite",
    "Oracle",
    "MongoDB",
    "Redis",
    "Firebase",
    "Cassandra",
    "Microsoft SQL Server",

    # Data / AI / ML
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Data Analysis",
    "Natural Language Processing",
    "Computer Vision",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "OpenCV",
    "Jupyter",
    "Generative AI",
    "Large Language Models",
    "LLM",

    # Cloud
    "AWS",
    "Microsoft Azure",
    "Google Cloud",
    "GCP",
    "Docker",
    "Kubernetes",
    "Jenkins",
    "Terraform",

    # DevOps / Tools
    "Git",
    "GitHub",
    "GitLab",
    "Bitbucket",
    "CI/CD",
    "Linux",
    "Unix",
    "Bash",
    "PowerShell",

    # APIs / Testing
    "REST API",
    "GraphQL",
    "Postman",
    "API Testing",
    "Unit Testing",
    "Integration Testing",
    "Selenium",
    "PyTest",
    "JUnit",

    # Automation / RPA
    "RPA",
    "UiPath",
    "Power Automate",
    "Automation Anywhere",

    # Microsoft / Office
    "Excel",
    "PowerPoint",
    "Word",

    # Mobile
    "Android",
    "Android Studio",
    "iOS",
    "Flutter",
    "React Native",

    # Software Engineering
    "Object Oriented Programming",
    "OOP",
    "Data Structures",
    "Algorithms",
    "Software Development",
    "Software Engineering",
    "SDLC",
    "STLC",

    # Other
    "Agile",
    "Scrum",
    "Jira",
    "Confluence",
]


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

# Existing project code imports SKILLS.
# Keep this name so we don't have to change other files.
SKILLS = SKILL_CATALOG


# ============================================================
# ALIASES
# ============================================================

ALIASES = {

    # Python
    "py": "Python",
    "python3": "Python",
    "python 3": "Python",

    # JavaScript
    "js": "JavaScript",
    "javascript es6": "JavaScript",
    "ecmascript": "JavaScript",

    # TypeScript
    "ts": "TypeScript",

    # C++
    "cpp": "C++",
    "c plus plus": "C++",

    # C#
    "c sharp": "C#",
    "csharp": "C#",

    # HTML
    "html5": "HTML",
    "hypertext markup language": "HTML",

    # CSS
    "css3": "CSS",
    "cascading style sheets": "CSS",

    # React
    "reactjs": "React",
    "react js": "React",

    # Angular
    "angularjs": "Angular",
    "angular js": "Angular",

    # Vue
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue js": "Vue.js",

    # Node
    "node": "Node.js",
    "nodejs": "Node.js",
    "node js": "Node.js",

    # Express
    "express": "Express.js",
    "expressjs": "Express.js",
    "express js": "Express.js",

    # SQL
    "structured query language": "SQL",

    # PostgreSQL
    "postgres": "PostgreSQL",
    "postgres database": "PostgreSQL",

    # MongoDB
    "mongo": "MongoDB",
    "mongodb database": "MongoDB",

    # Machine Learning
    "ml": "Machine Learning",
    "machine-learning": "Machine Learning",

    # Deep Learning
    "dl": "Deep Learning",
    "deep-learning": "Deep Learning",

    # Artificial Intelligence
    "ai": "Artificial Intelligence",
    "artificial-intelligence": "Artificial Intelligence",

    # Data Science
    "data-science": "Data Science",

    # NLP
    "nlp": "Natural Language Processing",
    "natural-language-processing": "Natural Language Processing",

    # Computer Vision
    "cv": "Computer Vision",
    "computer-vision": "Computer Vision",

    # Scikit-learn
    "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",

    # NumPy
    "numpy library": "NumPy",

    # Pandas
    "pandas library": "Pandas",

    # OpenCV
    "opencv": "OpenCV",
    "open cv": "OpenCV",

    # REST
    "rest": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",

    # Testing
    "api testing": "API Testing",
    "api tests": "API Testing",

    "pytest": "PyTest",
    "py test": "PyTest",

    # Cloud
    "amazon web services": "AWS",
    "google cloud platform": "GCP",

    # Kubernetes
    "k8s": "Kubernetes",

    # CI/CD
    "cicd": "CI/CD",
    "ci cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",

    # OOP
    "oops": "Object Oriented Programming",
    "object-oriented programming": "Object Oriented Programming",
    "object oriented programming": "Object Oriented Programming",

    # SDLC
    "software development life cycle": "SDLC",

    # STLC
    "software testing life cycle": "STLC",

    # Excel
    "ms excel": "Excel",
    "microsoft excel": "Excel",

    # PowerPoint
    "ms powerpoint": "PowerPoint",
    "microsoft powerpoint": "PowerPoint",

    # Word
    "ms word": "Word",
    "microsoft word": "Word",
}


# ============================================================
# DESCRIPTIVE WORDS
# ============================================================

DESCRIPTOR_WORDS = {
    "basic",
    "basics",
    "beginner",
    "beginners",
    "intermediate",
    "advanced",
    "proficient",
    "proficiency",
    "knowledge",
    "understanding",
    "experience",
    "experienced",
    "familiar",
    "familiarity",
    "working",
    "skills",
    "skill",
    "strong",
    "good",
    "excellent",
    "fundamentals",
    "fundamental",
    "level",
    "expert",
    "expertise",
    "hands-on",
    "handson",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _canonical_skill(value):
    """
    Convert one skill name into its canonical name.
    """

    if not value:
        return None

    value = str(value).strip()

    if not value:
        return None

    key = value.lower()

    # Alias
    if key in ALIASES:
        return ALIASES[key]

    # Catalog
    for skill in SKILL_CATALOG:
        if skill.lower() == key:
            return skill

    return None


def _add_unique(result, skill):
    """
    Add a skill only once.
    """

    if not skill:
        return

    skill = str(skill).strip()

    if not skill:
        return

    # Case-insensitive duplicate prevention
    existing = {
        item.lower()
        for item in result
    }

    if skill.lower() not in existing:
        result.append(skill)


def _clean_skill_text(text):
    """
    Remove words such as 'basic', 'advanced', 'knowledge',
    etc. while preserving actual skill names.
    """

    if not text:
        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if not text:
        return ""

    pattern = (
        r"\b(?:"
        + "|".join(
            re.escape(word)
            for word in sorted(
                DESCRIPTOR_WORDS,
                key=len,
                reverse=True
            )
        )
        + r")\b"
    )

    text = re.sub(
        pattern,
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def _split_skill_combinations(text):
    """
    Split combinations such as:

        HTML/CSS
        Python + Flask
        Java and Spring
        React & Node.js

    Do NOT split spaces because many skills contain
    multiple words.
    """

    if not text:
        return []

    return [
        part.strip()
        for part in re.split(
            r"\s*(?:/|\+|&|\band\b)\s*",
            text,
            flags=re.IGNORECASE
        )
        if part.strip()
    ]


def _find_catalog_skills_inside(text):
    """
    Find catalog skills inside a larger phrase.

    This is catalog-driven, not skill-specific.
    """

    if not text:
        return []

    text_lower = text.lower()

    found = []

    # Longer skills first.
    catalog = sorted(
        SKILL_CATALOG,
        key=len,
        reverse=True
    )

    for skill in catalog:

        skill_lower = skill.lower()

        pattern = (
            r"(?<![a-zA-Z0-9+#.])"
            + re.escape(skill_lower)
            + r"(?![a-zA-Z0-9+#.])"
        )

        if re.search(
            pattern,
            text_lower
        ):
            _add_unique(
                found,
                skill
            )

    # Aliases
    aliases = sorted(
        ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for alias, canonical in aliases:

        pattern = (
            r"(?<![a-zA-Z0-9+#.])"
            + re.escape(alias.lower())
            + r"(?![a-zA-Z0-9+#.])"
        )

        if re.search(
            pattern,
            text_lower
        ):
            _add_unique(
                found,
                canonical
            )

    return found


# ============================================================
# NORMALIZE SKILL LIST
# ============================================================

def normalize_skill_list(value):
    """
    Normalize skills into canonical individual skills.

    Examples:

        HTML/CSS
            -> HTML, CSS

        basic HTML/CSS
            -> HTML, CSS

        HTML and CSS
            -> HTML, CSS

        Python + Flask
            -> Python, Flask

        advanced Python
            -> Python

        machine learning
            -> Machine Learning

        REST API / Postman
            -> REST API, Postman
    """

    if not value:
        return []

    # --------------------------------------------------------
    # Convert input to chunks
    # --------------------------------------------------------

    if isinstance(
        value,
        (list, tuple, set)
    ):
        items = list(value)

    else:
        items = re.split(
            r"[,;\n|]+",
            str(value)
        )

    result = []

    # --------------------------------------------------------
    # Process each item
    # --------------------------------------------------------

    for item in items:

        if item is None:
            continue

        item = str(item).strip()

        if not item:
            continue

        item = re.sub(
            r"\s+",
            " ",
            item
        ).strip()

        # ----------------------------------------------------
        # Exact match FIRST.
        #
        # Important for:
        # Machine Learning
        # Data Science
        # REST API
        # Object Oriented Programming
        # ----------------------------------------------------

        canonical = _canonical_skill(item)

        if canonical:

            _add_unique(
                result,
                canonical
            )

            continue

        # ----------------------------------------------------
        # Remove descriptors.
        # ----------------------------------------------------

        cleaned = _clean_skill_text(item)

        if not cleaned:
            continue

        # ----------------------------------------------------
        # Check cleaned phrase.
        # ----------------------------------------------------

        canonical = _canonical_skill(cleaned)

        if canonical:

            _add_unique(
                result,
                canonical
            )

            continue

        # ----------------------------------------------------
        # Split combinations.
        # ----------------------------------------------------

        parts = _split_skill_combinations(
            cleaned
        )

        if not parts:
            parts = [cleaned]

        # ----------------------------------------------------
        # Process each part.
        # ----------------------------------------------------

        for part in parts:

            part = part.strip()

            if not part:
                continue

            # Remove unnecessary punctuation.
            part = re.sub(
                r"^[\s\-–—:]+|[\s\-–—:]+$",
                "",
                part
            ).strip()

            if not part:
                continue

            # -----------------------------------------------
            # Exact canonical/alias match
            # -----------------------------------------------

            canonical = _canonical_skill(part)

            if canonical:

                _add_unique(
                    result,
                    canonical
                )

                continue

            # -----------------------------------------------
            # Find known skills inside phrase
            # -----------------------------------------------

            found = _find_catalog_skills_inside(
                part
            )

            if found:

                for skill in found:

                    _add_unique(
                        result,
                        skill
                    )

                continue

            # -----------------------------------------------
            # Unknown skill
            #
            # Keep it rather than silently deleting it.
            # -----------------------------------------------

            words = []

            for word in part.split():

                if word.lower() not in DESCRIPTOR_WORDS:
                    words.append(word)

            unknown = " ".join(
                words
            ).strip()

            if unknown:

                _add_unique(
                    result,
                    unknown
                )

    return result


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(text):
    """
    Extract skills from free-form resume/JD text.

    This function is kept because the existing application
    imports it directly.

    It detects catalog skills and aliases from the entire text.
    """

    if not text:
        return []

    text = str(text)

    found = []

    text_lower = text.lower()

    # --------------------------------------------------------
    # Search catalog skills.
    # --------------------------------------------------------

    for skill in sorted(
        SKILL_CATALOG,
        key=len,
        reverse=True
    ):

        skill_lower = skill.lower()

        pattern = (
            r"(?<![a-zA-Z0-9+#.])"
            + re.escape(skill_lower)
            + r"(?![a-zA-Z0-9+#.])"
        )

        if re.search(
            pattern,
            text_lower
        ):

            _add_unique(
                found,
                skill
            )

    # --------------------------------------------------------
    # Search aliases.
    # --------------------------------------------------------

    for alias, canonical in sorted(
        ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):

        pattern = (
            r"(?<![a-zA-Z0-9+#.])"
            + re.escape(alias.lower())
            + r"(?![a-zA-Z0-9+#.])"
        )

        if re.search(
            pattern,
            text_lower
        ):

            _add_unique(
                found,
                canonical
            )

    return found


# ============================================================
# SINGLE SKILL NORMALIZATION
# ============================================================

def normalize_single_skill(skill):
    """
    Normalize one skill.

    Returns the first canonical skill found.
    """

    result = normalize_skill_list(
        [skill]
    )

    if result:
        return result[0]

    return None


# ============================================================
# SKILL COMPARISON
# ============================================================

def skills_match(
    candidate_skill,
    required_skill
):
    """
    Compare two skills after normalization.
    """

    candidate = normalize_single_skill(
        candidate_skill
    )

    required = normalize_single_skill(
        required_skill
    )

    if not candidate or not required:
        return False

    return (
        candidate.lower()
        ==
        required.lower()
    )


# ============================================================
# MATCHED / MISSING SKILLS
# ============================================================

def get_matched_and_missing_skills(
    candidate_skills,
    required_skills
):
    """
    Compare candidate skills against required skills.

    Returns:

        {
            "matched": [...],
            "missing": [...]
        }
    """

    candidate = normalize_skill_list(
        candidate_skills
    )

    required = normalize_skill_list(
        required_skills
    )

    candidate_lookup = {
        skill.lower(): skill
        for skill in candidate
    }

    matched = []
    missing = []

    for required_skill in required:

        key = required_skill.lower()

        if key in candidate_lookup:

            _add_unique(
                matched,
                required_skill
            )

        else:

            _add_unique(
                missing,
                required_skill
            )

    return {
        "matched": matched,
        "missing": missing
    }