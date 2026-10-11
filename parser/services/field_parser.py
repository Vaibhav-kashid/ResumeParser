"""Regex + keyword-based field extraction from raw resume text.

This is the core parsing engine. It is intentionally rule-based
(regex + a curated skills list) rather than ML-based, which keeps it
fast, dependency-light, and fully explainable — every extracted field
can be traced back to the pattern that matched it. spaCy (optional)
can be layered on top later for smarter name/organization detection;
see `ner_parser.py` stub for where that would plug in.
"""
import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\d{10}|\(?\d{3,4}\)?[-.\s]?\d{3}[-.\s]?\d{3,4})")
LINKEDIN_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_/]+", re.IGNORECASE)
GITHUB_RE = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_/]+", re.IGNORECASE)
YEAR_RE = re.compile(r"(19|20)\d{2}")

SECTION_HEADERS = {
    "education": ["education", "academic background", "academic qualification"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "skills": ["skills", "technical skills", "core competencies"],
    "certifications": ["certification", "certifications", "licenses"],
}

# Curated skill keyword list — the "predefined list" approach called
# for in the project spec. Extend this over time.
KNOWN_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "django", "flask",
    "fastapi", "react", "angular", "vue", "node.js", "html", "css", "bootstrap",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "git", "github", "docker",
    "kubernetes", "aws", "azure", "gcp", "linux", "rest api", "graphql",
    "machine learning", "deep learning", "nlp", "pandas", "numpy", "pyspark",
    "databricks", "tensorflow", "pytorch", "scikit-learn", "spacy", "excel",
    "power bi", "tableau", "agile", "scrum", "ci/cd", "jenkins",
]


def _split_into_sections(text):
    """Break resume text into {section_name: text_block} using header lines."""
    lines = text.split("\n")
    sections = {"header": []}
    current = "header"
    for line in lines:
        stripped = line.strip().lower().rstrip(":")
        matched_section = None
        for section, headers in SECTION_HEADERS.items():
            if stripped in headers:
                matched_section = section
                break
        if matched_section:
            current = matched_section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def _guess_name(text):
    """Best-effort: the first non-empty line that isn't an email/phone/URL
    and looks like a short line of words is usually the candidate's name."""
    for line in text.split("\n")[:6]:
        candidate = line.strip()
        if not candidate:
            continue
        if EMAIL_RE.search(candidate) or PHONE_RE.search(candidate):
            continue
        if len(candidate.split()) <= 5 and len(candidate) < 60:
            return candidate
    return ""


def parse_fields(text):
    """Parse raw resume text into a structured dict."""
    sections = _split_into_sections(text)
    header_and_all = text

    email_match = EMAIL_RE.search(header_and_all)
    phone_match = PHONE_RE.search(header_and_all)
    linkedin_match = LINKEDIN_RE.search(header_and_all)
    github_match = GITHUB_RE.search(header_and_all)

    found_skills = sorted({
        skill for skill in KNOWN_SKILLS
        if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE)
    })

    education_entries = _parse_education(sections.get("education", ""))
    experience_entries = _parse_experience(sections.get("experience", ""))

    return {
        "name": _guess_name(sections.get("header", text)),
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0).strip() if phone_match else "",
        "linkedin_url": ("https://" + linkedin_match.group(0)) if linkedin_match and not linkedin_match.group(0).startswith("http") else (linkedin_match.group(0) if linkedin_match else ""),
        "github_url": ("https://" + github_match.group(0)) if github_match and not github_match.group(0).startswith("http") else (github_match.group(0) if github_match else ""),
        "skills": found_skills,
        "education": education_entries,
        "experience": experience_entries,
    }


def _parse_education(block):
    entries = []
    for line in [l.strip() for l in block.split("\n") if l.strip()]:
        year_match = YEAR_RE.search(line)
        entries.append({
            "institution": line,
            "degree": "",
            "year": year_match.group(0) if year_match else "",
        })
    return entries[:10]


def _parse_experience(block):
    entries = []
    for line in [l.strip() for l in block.split("\n") if l.strip()]:
        entries.append({
            "company": "",
            "role": line,
            "duration": "",
            "description": "",
        })
    return entries[:10]
