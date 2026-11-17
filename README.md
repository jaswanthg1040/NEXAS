# NEXAs AI Interview — Master Build v4

This package is an enhanced continuation of the existing NEXAs v3 project, not a throw-away rewrite.

## Included
- Master / Creator / Learner role model (legacy `admin` database role is presented as Creator).
- Password authentication, email verification OTP, OTP login, forgot-password recovery.
- Permanent Interview Access Codes created by Creator; codes do not auto-expire but can be disabled. Learners must join that Creator's section before using its codes.
- Learners can also start independent practice interviews without an access code.
- Student/Section Join Codes connect learners to a Creator's section.
- PDF resumes are stored per learner, scored on upload, and can be rechecked from the resume library or dashboard.
- Self-introduction as the first real interview question.
- Text, Voice and Video interview UI with browser camera/microphone controls.
- Strict answer evaluation: empty, gibberish and clearly irrelevant answers score 0.
- Adaptive coaching and difficulty movement.
- Existing generated multi-branch question bank preserved and extended on startup.
- Performance profile and PDF reports.
- 3D anime-inspired hologram interviewer UI using pure CSS/JS; no 3D asset download is required.
- Responsive navigation with consistent NEXAs-styled action buttons.

## Run on Windows
1. Open PowerShell in this folder.
2. Create/activate a virtual environment if desired: `python -m venv .venv` then `.venv\Scripts\Activate.ps1`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set `SECRET_KEY`, `MASTER_EMAILS`, and `MASTER_PASSWORD`.
5. Run: `python app.py` or double-click `run.bat`.
6. Open `http://127.0.0.1:5000`.

## Important
The local interview evaluator is a deterministic fallback. The ATS score is a lightweight skills-keyword check, not a third-party hiring-system score. For production-grade interview AI scoring, configure `OPENAI_API_KEY` and `NEXA_AI_MODEL`. Browser speech recognition/TTS availability depends on the browser. Video behavior signals are UI/architecture hooks and should not be treated as medical or factual conclusions.

## Existing project continuity
The package retains the original Flask architecture, templates, static assets, database schema and question-bank generation approach from NEXA v3, while adding the master-plan features above.
