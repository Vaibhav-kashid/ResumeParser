# Resume Parser — Django Web App

A Django web application that accepts PDF/DOCX resumes, automatically
extracts candidate information (name, email, phone, skills, education,
LinkedIn/GitHub links), stores it in a database, and provides a
searchable candidate dashboard.

## Features

- User registration/login (Django auth)
- Resume upload (PDF, DOCX) with file-type and size validation
- Rule-based parsing engine (regex + curated skills keyword list)
- Candidate dashboard with search (name/email/phone) and skill filter
- Editable candidate profile (fix any misparsed fields)
- CSV export of all parsed candidates
- Django Admin panel for full record management

## Tech Stack

Python, Django, SQLite (dev) / MySQL-ready, pdfplumber, python-docx,
Bootstrap 5.

## Project Structure

```
resume_parser_project/   # Django project settings & root urls
accounts/                 # Signup / login / logout
parser/                   # Upload, parsing engine, candidate models
  services/
    text_extraction.py    # PDF/DOCX -> raw text
    field_parser.py        # raw text -> structured fields (regex)
    resume_service.py      # orchestrates extract -> parse -> save
dashboard/                 # Candidate list, search, CSV export
templates/                 # Bootstrap-based HTML templates
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` — you'll be redirected to the login
page. Sign up for a new account, then upload a resume.

## Switching to MySQL

Replace the `DATABASES` block in `resume_parser_project/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'resume_parser_db',
        'USER': 'root',
        'PASSWORD': '<your-password>',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Install the connector: `pip install mysqlclient`, then re-run
`python manage.py migrate`.

## How Parsing Works

1. `text_extraction.py` pulls raw text out of the uploaded PDF
   (pdfplumber) or DOCX (python-docx), including table cells.
2. `field_parser.py` splits the text into sections using common
   resume headers (Education, Experience, Skills, Certifications),
   then applies regex patterns for email/phone/LinkedIn/GitHub and
   matches against a curated skills keyword list.
3. `resume_service.py` saves everything to the database as a
   `Candidate` with related `Education`, `Experience`, and `Skill`
   rows, and marks the upload as `parsed` or `failed`.

## Known Limitations / Next Steps

- No OCR — scanned (image-only) PDFs without a text layer aren't
  supported yet (pytesseract would be the next addition).
- Education/Experience parsing is line-based, not deeply structured
  (works well for standard formats, less well for creative layouts).
- Advanced features from the original spec (ATS scoring, JD matching,
  duplicate detection, AI-generated summaries) are intentionally left
  as stretch goals for a v2 — see the project guide document.
