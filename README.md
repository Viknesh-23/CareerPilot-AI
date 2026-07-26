# CareerPilot AI

CareerPilot AI is a production-minded Flask platform for managing the job-application lifecycle: it tracks applications, compares resumes to job descriptions, identifies skill gaps, calculates readiness, and supports application-specific mock interviews.

> Live demo: add your Render URL here after deployment.

## Highlights

- Secure registration, sign-in, per-user data isolation, CSRF protection, hashed passwords, and PDF upload validation.
- Complete application CRUD, filtering/search/sorting, CSV export, activity timeline, interview events, and drag-and-drop Kanban workflow.
- Multiple text-PDF resumes with PyMuPDF extraction; normalized ATS matching against curated skills and aliases.
- Cross-application skill-demand and skill-gap analysis, with a transparent readiness score.
- AI-assisted (Gemini) or deterministic local fallback interview question generation and answer evaluation.
- Mock interview reports, ATS reports, and downloadable PDFs built with ReportLab.
- Dashboard and analytics charts powered by Chart.js; responsive Bootstrap UI with persisted dark mode.

## Architecture

```text
Browser → Flask blueprints → service layer → SQLAlchemy models → SQLite/PostgreSQL
                              ├─ PyMuPDF (resume text)
                              ├─ Gemini (optional)
                              └─ ReportLab (PDF reports)
```

Routes are intentionally thin. Resume parsing, ATS matching, skill-gap calculation, readiness scoring, Gemini fallback behavior, interview evaluation, and PDF construction live in `services/`.

## Project structure

```text
CareerPilot-AI/
├── app.py                 # application factory and CLI
├── config.py              # environment-first configuration
├── models/                # User, application, resume, interview entities
├── routes/                # Flask blueprints
├── services/              # business and AI-integration services
├── templates/             # Bootstrap/Jinja screens
├── static/                # CSS and Chart.js / Kanban scripts
├── scripts/seed_data.py   # local fake demo data
└── tests/                 # pytest suite
```

## Local setup

```bash
git clone <repository-url>
cd CareerPilot-AI
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env  # Windows; use cp .env.example .env on macOS/Linux
flask --app app init-db
flask --app app run
```

Open `http://127.0.0.1:5000`. SQLite is selected automatically if `DATABASE_URL` is unset.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | Production | Signs sessions and CSRF tokens. Use a strong random value. |
| `DATABASE_URL` | Production | SQLAlchemy URL; Render PostgreSQL is supported. |
| `GEMINI_API_KEY` | No | Enables Gemini-generated questions and answer evaluation. |
| `MAX_CONTENT_LENGTH` | No | Upload limit in bytes (defaults to 8 MiB). |

`config.py` converts legacy `postgres://` URLs to `postgresql://` for SQLAlchemy compatibility. Never commit `.env`.

## Database initialization and migrations

For a new local database:

```bash
flask --app app init-db
```

Flask-Migrate is configured for schema evolution:

```bash
flask --app app db init       # first time only
flask --app app db migrate -m "initial schema"
flask --app app db upgrade
```

## ATS scoring

The ATS service uses a curated technical/professional vocabulary, case normalization, skill aliases (`js → javascript`, `postgres → postgresql`, `ml → machine learning`), and word-boundary matching. The score is the percentage of recognized JD skills that occur in the resume; it deliberately does not score every common word.

## Job readiness formula

```text
Readiness = ATS Match × 0.30
          + Skill Coverage × 0.25
          + Interview Preparation × 0.25
          + Profile Completion × 0.20
```

The final result is clamped to 0–100. Interview preparation is derived from answered generated questions, while skill coverage compares user-profile and resume skills to the tracked job descriptions.

## Gemini integration and fallback

When `GEMINI_API_KEY` is set, `services/gemini_service.py` uses the current `google-genai` SDK for question generation and evaluation. Any missing key, quota problem, unavailable model, or network failure transparently falls back to local role-aware questions and a deterministic answer rubric based on answer detail, relevance, technical evidence, and STAR structure. The product remains useful without Gemini.

## Testing

```bash
pytest
```

Tests use a temporary SQLite database and cover authentication, ownership controls, application CRUD/status history/CSV export, PDF upload handling, ATS normalization and score range, readiness arithmetic, fallback answer evaluation, and the full interview workflow.

## Fake demo data

```bash
python scripts/seed_data.py
```

This creates a clearly fictional local-only account:

```text
Email: demo@careerpilot.local
Password: DemoPass123!
```

Do not use it in production.

## Render deployment

1. Push the repository to GitHub and create a new Render Blueprint from it.
2. Render reads `render.yaml`, provisions PostgreSQL, sets `DATABASE_URL`, and starts `gunicorn app:app`.
3. Set `GEMINI_API_KEY` in the Render environment only if you want live Gemini assistance.
4. Run migrations with a Render shell (`flask --app app db upgrade`) after creating migration files, or use `flask --app app init-db` for an initial simple deployment.
5. Set a strong `SECRET_KEY` (the blueprint generates one by default).

## Manual verification flow

1. Register an account and complete the career profile.
2. Upload a text-based PDF resume.
3. Create a job application with a job description.
4. Run ATS matching, inspect gaps, and download the report.
5. Move the application in the Kanban board; confirm its activity timeline updates.
6. Schedule an interview event, generate prep questions, complete the mock interview, and download its report.
7. Review dashboard, analytics, and export the application CSV.
8. Repeat step 6 without `GEMINI_API_KEY` to confirm the local fallback behavior.

## Security notes

Passwords use Werkzeug hashing. Every resource lookup confirms ownership before reading or modifying it. CSRF protection is enabled, files are named with `secure_filename`, PDFs are checked before text extraction, uploads have an application-level size limit, and configuration secrets are environment-based.

## Future improvements

Email reminders, calendar sync, OCR for scanned resumes, role-specific scoring profiles, richer dashboard filtering, and asynchronous job processing are sensible future additions.

## License

MIT — add a `LICENSE` file before publishing if you want to distribute the project under this license.
