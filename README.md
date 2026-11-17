# NEXAs AI Interview

NEXAs is a Flask application for technical interview practice and interview management. Learners can practise independently or use a Creator's interview code. The interface uses Jinja templates, CSS, and browser JavaScript APIs; application data is stored in SQLite.

## Features

- **Three account roles:** Learner, Creator (stored as the legacy `admin` role), and Master.
- **Account flows:** password sign-in, email verification, OTP sign-in, and OTP-based password reset.
- **Sections:** Creators can create sections and share a Student Join Code with learners.
- **Interview access:** Learners can start solo practice or use an enabled interview code issued by their section's Creator. Creators can disable codes.
- **Interview setup:** six technical branches (AIML, CSE, Data Science, Cyber Security, ECE, and EEE), three difficulty levels, and Text, Voice, or Video modes.
- **Question bank:** generated branch-and-level questions are seeded into SQLite at startup; the interview begins with a self-introduction question.
- **Answer evaluation:** a local evaluator is available, with optional OpenAI evaluation when configured. Evaluation includes correctness, clarity, structure, depth, and confidence indicators; adaptive follow-up questions and difficulty changes are supported.
- **Resume library:** learners can upload text-readable PDF resumes, view a lightweight skills-keyword ATS estimate, recheck it, and download their stored file.
- **Progress and reports:** interview results, learner performance summaries, and downloadable PDF reports.
- **Creator and Master tools:** section, learner, question-bank, interview-code, and platform-account management. Master can also configure Creator permissions.
- **Interview UI:** browser speech recognition/synthesis where supported, camera/microphone preview for Video mode, and a CSS/JavaScript anime-inspired hologram. Browser permissions and API support are required for media features.
- **Help endpoint:** provides short in-app answers about common account and interview topics.

The ATS score is a simple keyword estimate, not a score from a commercial applicant-tracking system. Camera/microphone behavior events are stored as application events; they are not medical or factual assessments.

## Requirements

- Python 3
- `pip`
- A modern browser for the web interface
- Optional: an OpenAI API key for AI-assisted answer evaluation
- Optional: SMTP account settings to send OTP emails

Python packages are listed in [`requirements.txt`](requirements.txt): Flask, python-dotenv, Werkzeug, ReportLab, pypdf, and OpenAI.

## Run on Windows

From the project directory, either double-click `run.bat` or run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set the values described below.
python app.py
```

Open <http://127.0.0.1:5000>. `run.bat` creates `.venv` if needed, installs requirements, and starts the app.

## Run on macOS or Linux

```bash
cp .env.example .env
# Edit .env and set the values described below.
chmod +x run.sh
./run.sh
```

`run.sh` creates `.venv` if needed, installs requirements, and starts the app. Alternatively, create and activate a virtual environment manually, install `requirements.txt`, and run `python app.py`.

## Configuration

Copy `.env.example` to `.env`. The `.env` file is ignored by Git; do not commit real credentials.

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Flask session-signing key. Set a long, unique random value. The built-in fallback is for local development only. |
| `NEXA_DB` | SQLite database path; defaults to `/tmp/nexa.db`. Set this to a durable path for deployments where temporary storage is cleared on restart. |
| `MASTER_EMAILS` | Comma-separated email addresses provisioned as Master accounts at startup. |
| `MASTER_PASSWORD` | Password for the configured Master email addresses. Set a non-default password. |
| `OPENAI_API_KEY` | Optional key for AI-assisted evaluation. Leave blank to use the local evaluator. |
| `NEXA_AI_MODEL` | Optional model name used by the AI evaluation configuration. |
| `OPENAI_MODEL` | Optional model-name setting retained for compatibility with the project configuration. |
| `SMTP_HOST` | SMTP server hostname; the app defaults to `smtp.gmail.com` when sending email. |
| `SMTP_PORT` | SMTP port; defaults to `587`. |
| `SMTP_USERNAME` | SMTP login username. |
| `SMTP_PASSWORD` | SMTP login password or app password. |
| `SMTP_FROM` | Optional sender address; defaults to `SMTP_USERNAME`. |

When SMTP credentials are not configured, OTPs are printed to the application console for local development. Do not rely on that behavior for a deployed service.

## Main routes

- `/` — home page
- `/register`, `/login`, `/verify` — account registration and sign-in
- `/request-login-otp`, `/verify-login-otp` — OTP sign-in
- `/forgot-password`, `/reset-password` — password recovery
- `/dashboard`, `/student/join` — learner dashboard and section joining
- `/interview`, `/interview/take` — interview setup and session
- `/resume` — PDF resume library and ATS estimate
- `/profile`, `/result/<id>`, `/report/<id>` — performance, results, and PDF report
- `/admin` (also `/creator`) — Creator Studio
- `/master` — Master console; Master sign-in is at `/nexa-core-access`
- `/api/evaluate-answer`, `/api/adaptive-question`, `/api/behavior-event` — interview APIs
- `/help` — in-app help API

## Project layout

```text
.
├── app.py                    # Flask routes, SQLite schema, question bank, evaluation, reports
├── requirements.txt          # Python dependencies
├── .env.example              # Environment-variable template
├── .gitignore                # Excludes local environment, database, and generated files
├── .vscode/settings.json     # VS Code Python terminal setting
├── run.bat                   # Windows setup and launch script
├── run.sh                    # macOS/Linux setup and launch script
├── PROJECT_VERSION.txt       # Version and release summary
├── CHANGELOG_V4.md           # Version 4 feature notes
├── MASTER_NEXAS_PLAN.md      # Product and architecture plan
├── static/
│   ├── anime.css, anime.js   # Hologram interviewer presentation
│   ├── style.css             # Main application styling
│   ├── script.js             # Shared browser interactions
│   ├── upgrade.css           # Additional interface styling
│   └── upgrade.js            # Additional interface behavior
└── templates/                # Jinja pages for auth, learner, Creator, and Master flows
```

The `templates/` directory contains `admin.html`, `auth.html`, `base.html`, `dashboard.html`, `error.html`, `forgot_password.html`, `home.html`, `interview_setup.html`, `login_otp.html`, `master.html`, `master_login.html`, `otp.html`, `profile.html`, `reset_password.html`, `result.html`, `resume.html`, and `take.html`.

The configured SQLite database, `.env`, `.venv/`, and Python cache files are local/runtime data and are excluded from Git. The default `/tmp/nexa.db` location is temporary on many hosts; set `NEXA_DB` to a persistent path if database contents must survive restarts. The database is initialized and migrated by `app.py` when the application starts; resume PDFs and interview records are stored in that database.

## Development and deployment notes

- Run the app from the project directory so the default relative database path resolves as expected.
- `app.py` starts Flask with debug mode enabled when run directly. This is a development setup, not a production server configuration.
- Configure a strong `SECRET_KEY`, Master credentials, and SMTP settings before using real accounts. Keep secrets out of source control.
- Browser speech recognition, text-to-speech, camera, and microphone support varies by browser and may require a secure context outside localhost.
- No automated test suite is included in this repository.
