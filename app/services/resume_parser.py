import re


# ============================================================
# LOCATION DATA
# ============================================================

LOCATION_WORDS = {
    "gurugram", "gurgaon", "delhi", "new delhi", "noida", "greater noida",
    "faridabad", "ghaziabad", "jaipur", "chandigarh", "mumbai", "pune",
    "bengaluru", "bangalore", "hyderabad", "chennai", "kolkata", "ahmedabad",
    "surat", "lucknow", "bhopal", "indore", "patna", "ranchi", "dehradun",
    "agra", "amritsar", "ludhiana", "kochi", "coimbatore", "mysuru", "mysore",
    "india", "haryana", "punjab", "rajasthan", "maharashtra", "karnataka",
    "telangana", "tamil nadu", "uttar pradesh", "uttarakhand", "gujarat",
    "kerala", "bihar", "jharkhand", "madhya pradesh",
    "uttaranchal", "andhra pradesh", "odisha", "orissa",
    "west bengal", "goa", "sikkim", "assam", "meghalaya"
}


# ============================================================
# WORDS THAT MUST NEVER BECOME A CANDIDATE NAME
# ============================================================

BAD_NAME_WORDS = {
    "resume",
    "curriculum vitae",
    "cv",
    "profile",
    "contact",
    "contact information",
    "personal information",
    "personal details",
    "professional summary",
    "summary",
    "objective",
    "career objective",
    "career summary",
    "career profile",
    "professional profile",
    "personal profile",
    "education",
    "experience",
    "work experience",
    "professional experience",
    "employment",
    "employment history",
    "skills",
    "technical skills",
    "soft skills",
    "projects",
    "academic projects",
    "personal projects",
    "certifications",
    "certificates",
    "achievements",
    "languages",
    "interests",
    "hobbies",
    "references",
    "internship",
    "internships",
    "python developer",
    "software developer",
    "web developer",
    "full stack developer",
    "backend developer",
    "frontend developer",
    "developer",
    "student",
    "about me",
    "qualification",
    "qualifications",
    "academic profile",
    "academic background",
    "professional background",
    "work history",
}


# ============================================================
# REGEX
# ============================================================

NAME_LABEL_RE = re.compile(
    r"^(?:name|candidate\s*name|full\s*name)\s*[:\-]\s*(.+)$",
    re.I
)

PHONE_RE = re.compile(
    r"(?:\+?91[\s\-]?)?(?:\(?\d{3,5}\)?[\s\-]?)?\d{5}[\s\-]?\d{5}"
)

EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)

LINKEDIN_RE = re.compile(
    r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9._%-]+",
    re.I
)

GITHUB_RE = re.compile(
    r"https?://(?:www\.)?github\.com/[A-Za-z0-9._-]+",
    re.I
)

HEADING_RE = re.compile(
    r"^(?:"
    r"summary|professional\s+summary|profile|professional\s+profile|"
    r"objective|career\s+objective|career\s+summary|"
    r"contact|contact\s+information|personal\s+information|"
    r"education|academic\s+background|qualification|qualifications|"
    r"experience|work\s+experience|professional\s+experience|"
    r"employment|employment\s+history|"
    r"skills|technical\s+skills|soft\s+skills|"
    r"projects|academic\s+projects|personal\s+projects|"
    r"certifications?|certificates?|"
    r"achievements?|languages?|interests?|hobbies?|references?"
    r")\s*:?\s*$",
    re.I
)


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_text(path):
    """
    Extract text from PDF or DOCX.
    """

    path = str(path)

    if path.lower().endswith(".pdf"):
        import pdfplumber

        pages = []

        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                try:
                    text = page.extract_text() or ""
                except Exception:
                    text = ""

                if text:
                    pages.append(text)

        return "\n".join(pages).strip()

    if path.lower().endswith(".docx"):
        from docx import Document

        document = Document(path)

        parts = []

        for paragraph in document.paragraphs:
            text = paragraph.text.strip()
            if text:
                parts.append(text)

        # Also inspect tables because some resumes store
        # contact information inside tables.
        for table in document.tables:
            for row in table.rows:
                values = []

                for cell in row.cells:
                    value = cell.text.strip()
                    if value:
                        values.append(value)

                if values:
                    parts.append(" | ".join(values))

        return "\n".join(parts).strip()

    raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")


# ============================================================
# EMAIL
# ============================================================

def extract_email(text):
    match = EMAIL_RE.search(text or "")

    if match:
        return match.group(0).strip()

    return ""


# ============================================================
# PHONE
# ============================================================

def extract_phone(text):
    text = text or ""

    patterns = [
        r"(?<!\d)\+91[\s\-]?[6-9]\d{9}(?!\d)",
        r"(?<!\d)91[\s\-]?[6-9]\d{9}(?!\d)",
        r"(?<!\d)[6-9]\d{9}(?!\d)",
        r"(?<!\d)\+91[\s\-]?\d{5}[\s\-]\d{5}(?!\d)",
        r"(?<!\d)\d{5}[\s\-]\d{5}(?!\d)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0).strip()

    return ""


# ============================================================
# LINKEDIN
# ============================================================

def extract_linkedin(text):
    match = LINKEDIN_RE.search(text or "")

    if match:
        return match.group(0).strip()

    # Handle linkedin.com/in/... without https
    match = re.search(
        r"(?:www\.)?linkedin\.com/in/[A-Za-z0-9._%-]+",
        text or "",
        re.I
    )

    if match:
        return "https://" + match.group(0).strip()

    return ""


# ============================================================
# GITHUB
# ============================================================

def extract_github(text):
    match = GITHUB_RE.search(text or "")

    if match:
        return match.group(0).strip()

    match = re.search(
        r"(?:www\.)?github\.com/[A-Za-z0-9._-]+",
        text or "",
        re.I
    )

    if match:
        return "https://" + match.group(0).strip()

    return ""


# ============================================================
# NAME CLEANING
# ============================================================

def _clean_name(value):
    """
    Aggressively clean a possible candidate name.
    """

    if not value:
        return ""

    value = value.strip()

    # Remove bullets
    value = re.sub(
        r"^[•▪●◦○\-*–—]+\s*",
        "",
        value
    )

    # Remove explicit name labels
    value = re.sub(
        r"^(?:name|candidate\s*name|full\s*name)\s*[:\-]\s*",
        "",
        value,
        flags=re.I
    )

    # Remove email
    value = EMAIL_RE.sub("", value)

    # Remove LinkedIn/GitHub URLs
    value = LINKEDIN_RE.sub("", value)
    value = GITHUB_RE.sub("", value)

    # Remove phone numbers
    value = re.sub(
        r"(?:\+?91[\s\-]?)?(?:\(?\d{3,5}\)?[\s\-]?)?\d{5}[\s\-]?\d{5}",
        " ",
        value
    )

    # Remove common trailing labels.
    # Example:
    # "Simran Chawla SUMMARY"
    # "Nisha Verma Profile"
    # "Rahul Sharma Objective"
    value = re.sub(
        r"\s+(?:summary|profile|objective|contact|"
        r"professional\s+summary|career\s+objective|"
        r"technical\s+skills)\s*$",
        "",
        value,
        flags=re.I
    )

    # Remove job titles if they appear after separators.
    # Example:
    # "Nisha Verma | Python Developer"
    # "Rahul Sharma - Software Engineer"
    value = re.split(
        r"\s+[|•]\s+|\s+[–—]\s+|\s+\|\s+",
        value,
        maxsplit=1
    )[0]

    # Remove content after obvious contact labels.
    value = re.split(
        r"\b(?:email|phone|mobile|linkedin|github|address)\b\s*[:\-]?",
        value,
        maxsplit=1,
        flags=re.I
    )[0]

    # Keep only letters, spaces, apostrophes, periods and hyphens.
    value = re.sub(
        r"[^A-Za-zÀ-ÖØ-öø-ÿ\s.'-]",
        " ",
        value
    )

    # Collapse spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip(" .-_")


# ============================================================
# NAME VALIDATION
# ============================================================

def _valid_name(value):
    """
    Decide whether a string looks like a real person's name.
    """

    value = _clean_name(value)

    if not value:
        return False

    low = value.lower().strip()

    if low in BAD_NAME_WORDS:
        return False

    if HEADING_RE.match(low):
        return False

    words = low.split()

    # Most Indian full names will have 2-4 words.
    if not (2 <= len(words) <= 4):
        return False

    # Reject locations.
    for word in words:
        if word in LOCATION_WORDS:
            return False

    # Reject common resume terms.
    bad_fragments = [
        "linkedin",
        "github",
        "email",
        "phone",
        "mobile",
        "address",
        "summary",
        "objective",
        "experience",
        "education",
        "skills",
        "project",
        "certification",
        "developer",
        "engineer",
        "student",
    ]

    for fragment in bad_fragments:
        if fragment in low:
            return False

    # A person's name should contain alphabetic words.
    for word in words:
        if not re.fullmatch(
            r"[A-Za-zÀ-ÖØ-öø-ÿ][A-Za-zÀ-ÖØ-öø-ÿ.'-]*",
            word
        ):
            return False

    # Avoid very long names.
    if len(value) > 40:
        return False

    return True


# ============================================================
# NAME EXTRACTION
# ============================================================

def extract_name(text):
    """
    Extract the candidate's name from a resume.

    Priority:
    1. Explicit "Name:" field
    2. First clean name-like line
    3. Name before contact information
    """

    if not text:
        return "Unknown Candidate"

    raw_lines = text.splitlines()

    lines = []

    for raw in raw_lines:
        line = re.sub(r"\s+", " ", raw).strip()

        if line:
            lines.append(line)

    # --------------------------------------------------------
    # STEP 1: Explicit name label
    # --------------------------------------------------------

    for line in lines[:40]:

        match = NAME_LABEL_RE.match(line)

        if match:
            candidate = _clean_name(match.group(1))

            if _valid_name(candidate):
                return candidate

    # --------------------------------------------------------
    # STEP 2: Look at first 20 lines
    # --------------------------------------------------------

    candidates = []

    for index, line in enumerate(lines[:25]):

        # Skip obvious headings.
        if HEADING_RE.match(line):
            continue

        cleaned = _clean_name(line)

        if not cleaned:
            continue

        if not _valid_name(cleaned):
            continue

        words = cleaned.split()

        score = 0

        # Names with 2-3 words are highly likely.
        if len(words) == 2:
            score += 5

        elif len(words) == 3:
            score += 4

        elif len(words) == 4:
            score += 2

        # Names near the top are more likely.
        if index == 0:
            score += 5

        elif index <= 2:
            score += 4

        elif index <= 5:
            score += 2

        # Title Case is common for names.
        if cleaned == cleaned.title():
            score += 2

        # Short lines are more likely names.
        if len(cleaned) <= 30:
            score += 2

        # If original line contained contact information,
        # the cleaned result may still be a valid name.
        if EMAIL_RE.search(line):
            score += 1

        if PHONE_RE.search(line):
            score += 1

        candidates.append(
            (score, -index, cleaned)
        )

    if candidates:
        candidates.sort(reverse=True)

        return candidates[0][2]

    # --------------------------------------------------------
    # STEP 3: Special fallback
    # --------------------------------------------------------

    # Search for a line that contains a likely name followed
    # by contact information.
    for line in lines[:15]:

        candidate = line

        candidate = EMAIL_RE.sub("", candidate)

        candidate = re.sub(
            r"(?:\+?91[\s\-]?)?(?:\(?\d{3,5}\)?[\s\-]?)?\d{5}[\s\-]\d{5}",
            "",
            candidate
        )

        candidate = _clean_name(candidate)

        if _valid_name(candidate):
            return candidate

    return "Unknown Candidate"


# ============================================================
# LOCATION
# ============================================================

def extract_location(text):
    """
    Extract location from the beginning/contact section.
    """

    if not text:
        return ""

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # First search for explicit location/address labels.
    for line in lines[:40]:

        match = re.match(
            r"^(?:location|address|based in|city)\s*[:\-]\s*(.+)$",
            line,
            flags=re.I
        )

        if match:
            value = match.group(1).strip()

            if value:
                return value

    # Search for city/state combinations.
    for line in lines[:35]:

        low = line.lower()

        if "@" in line:
            continue

        if "linkedin" in low or "github" in low:
            continue

        found = False

        for location in LOCATION_WORDS:
            if re.search(
                r"\b" + re.escape(location) + r"\b",
                low
            ):
                found = True
                break

        if found and len(line) <= 100:
            return line

    return ""


# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience_years(text):
    """
    Extract total professional experience.

    Examples:
        2 years experience -> 2
        1.5 years -> 1.5
        6 months -> 0.5
        Fresher -> 0
        0-1 years -> 0.5
    """

    if not text:
        return 0.0

    full_text = text.lower()

    section = _section(
        text,
        {
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "employment",
            "internship",
            "internships"
        }
    )

    source = section if section else full_text

    # --------------------------------------------------------
    # Explicit "X years experience"
    # --------------------------------------------------------

    patterns = [
        r"(?:total\s+)?(?:professional\s+)?experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",

        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+of\s+(?:professional\s+)?experience",

        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s+(?:professional\s+)?experience",

        r"experience\s*[:\-]\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            full_text,
            flags=re.I
        )

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    # --------------------------------------------------------
    # X-Y years
    # --------------------------------------------------------

    range_matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(?:-|–|—|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b",
        source,
        flags=re.I
    )

    if range_matches:

        values = []

        for start, end in range_matches:

            try:
                start_value = float(start)
                end_value = float(end)

                values.append(
                    (start_value + end_value) / 2
                )

            except ValueError:
                continue

        if values:
            return max(values)

    # --------------------------------------------------------
    # Months
    # --------------------------------------------------------

    month_matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(?:months?|mos?)\b",
        source,
        flags=re.I
    )

    month_values = []

    for value in month_matches:

        try:
            months = float(value)

            if 0 <= months <= 240:
                month_values.append(months / 12)

        except ValueError:
            continue

    # --------------------------------------------------------
    # Years
    # --------------------------------------------------------

    year_matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b",
        source,
        flags=re.I
    )

    year_values = []

    for value in year_matches:

        try:
            years = float(value)

            # Ignore obviously invalid values.
            if 0 <= years <= 50:
                year_values.append(years)

        except ValueError:
            continue

    if year_values:
        return max(year_values)

    if month_values:
        return max(month_values)

    return 0.0


# ============================================================
# SECTION EXTRACTION
# ============================================================

def _section(text, names):
    """
    Return the text belonging to a resume section.
    """

    if not text:
        return ""

    lines = text.splitlines()

    normalized_names = {
        re.sub(r"\s+", " ", name.lower()).rstrip(":")
        for name in names
    }

    start = None

    for index, line in enumerate(lines):

        normalized = re.sub(
            r"\s+",
            " ",
            line.strip().lower()
        ).rstrip(":")

        if normalized in normalized_names:
            start = index + 1
            break

    if start is None:
        return ""

    section_headers = {
        "education",
        "academic background",
        "education qualification",
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "skills",
        "technical skills",
        "soft skills",
        "projects",
        "academic projects",
        "personal projects",
        "certifications",
        "certificates",
        "certification",
        "achievements",
        "languages",
        "interests",
        "hobbies",
        "references",
        "internship",
        "internships",
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
    }

    output = []

    for line in lines[start:]:

        normalized = re.sub(
            r"\s+",
            " ",
            line.strip().lower()
        ).rstrip(":")

        if normalized in section_headers:
            break

        output.append(line)

    return "\n".join(output).strip()


# ============================================================
# EDUCATION
# ============================================================

def extract_education(text):
    """
    Extract education section or detect common degrees.
    """

    section = _section(
        text,
        {
            "education",
            "academic background",
            "education qualification",
            "qualifications"
        }
    )

    if section:
        return section

    patterns = [
        r"(?i)\bB\.?\s*Tech\b[^\n]*",
        r"(?i)\bB\.?\s*E\.?\b[^\n]*",
        r"(?i)\bBachelor(?:'s)?\s+(?:of|in)\b[^\n]*",
        r"(?i)\bM\.?\s*Tech\b[^\n]*",
        r"(?i)\bMCA\b[^\n]*",
        r"(?i)\bBCA\b[^\n]*",
        r"(?i)\bB\.?\s*Sc\.?\b[^\n]*",
        r"(?i)\bM\.?\s*Sc\.?\b[^\n]*",
        r"(?i)\bBachelor[^\n]*Computer Science[^\n]*",
        r"(?i)\bBachelor[^\n]*Information Technology[^\n]*",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text or ""
        )

        if match:
            return match.group(0).strip()

    return ""


# ============================================================
# PROJECTS
# ============================================================

def extract_projects(text):
    return _section(
        text,
        {
            "projects",
            "academic projects",
            "personal projects"
        }
    )


# ============================================================
# CERTIFICATIONS
# ============================================================

def extract_certifications(text):
    return _section(
        text,
        {
            "certifications",
            "certificates",
            "certification"
        }
    )


# ============================================================
# GRADUATION YEAR
# ============================================================

def extract_graduation_year(text):
    """
    Detect graduation year.

    Looks for years from 2010 onward and returns the latest
    reasonable year.
    """

    if not text:
        return None

    years = []

    for value in re.findall(
        r"\b(20(?:1\d|2\d))\b",
        text
    ):

        try:
            year = int(value)

            if 2010 <= year <= 2035:
                years.append(year)

        except ValueError:
            continue

    if not years:
        return None

    return max(years)