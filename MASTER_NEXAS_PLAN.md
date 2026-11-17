# NEXAs AI Interview — Master Project Plan

## Product
NEXAs is a secure AI interview platform with three roles: Master, Creator and Learner. The build continues the existing Flask NEXAs project.

## Core rules
1. Master has platform-wide authority.
2. Creator permissions are controlled by Master and checked on the backend.
3. Learners enter Creator-generated Interview Access Codes.
4. Interview Access Codes do not automatically expire. Master/Creator can disable them.
5. Every interview begins with a real Self Introduction question.
6. Text, Voice and Video modes use the same evaluation principles.
7. Empty, gibberish and clearly irrelevant answers receive 0.
8. Client validation is never trusted as the only validation layer.
9. Interview state prevents duplicate/late submissions.
10. Behavioral signals are observations, not diagnoses or accusations.

## Architecture
- Flask application
- SQLite for local development
- Jinja templates
- CSS/JavaScript frontend
- Optional OpenAI integration through environment variables
- Browser SpeechRecognition / SpeechSynthesis for voice
- Browser getUserMedia for video/audio
- ReportLab PDF reporting

## Roles
### Master
Manage Creators, permissions, branches/question bank, interviews, learners, results, audit logs and platform settings.

### Creator
Create interview configurations, generate permanent Interview Access Codes, manage assigned learners/sections and curate questions. Permissions include create_interviews, manage_questions, manage_learners, view_results and export_reports.

### Learner
Register/login, optionally join a section, enter an Interview Access Code, complete device checks, answer Self Introduction and technical questions, and receive the configured report.

## Authentication
- Password login
- OTP login
- Email verification OTP
- Forgot password + reset OTP
- Server-side OTP verification
- Previous OTP invalidation
- Secure password hashing

## Interview lifecycle
NOT_STARTED → READY → IN_PROGRESS → EVALUATING → COMPLETED → EVALUATED

## Question bank
The existing generated multi-branch bank is retained. The current generation strategy produces 300 questions per branch/level combination across the configured branches and levels, while the architecture remains metadata-driven and extensible.

Each question supports branch, level, topic context, answer evaluation and adaptive follow-up behavior.

## Strict evaluation
Evaluation dimensions:
- correctness
- relevance
- clarity
- structure
- depth
- confidence indicator

Meaningless answers such as repeated nonsense, filler-only responses or clearly unrelated short answers are explicitly zeroed before normal scoring.

## Media
### Text
Question → answer → validation → evaluation → feedback.

### Voice
Speech → browser STT → answer text → validation/evaluation. AI questions can be spoken with browser TTS.

### Video
Camera + microphone preview → voice pipeline → answer evaluation. The UI includes a 3D anime-inspired holographic interviewer. Behavioral-event storage is provided for future vision/behavior models.

## 3D anime experience
The project uses a pure CSS 3D anime-inspired hologram so the project remains easy to run without downloading a large proprietary 3D model. The character includes layered hair, face, eyes, body, holographic orbit rings, glow and pointer-responsive movement.

For a future production version, the CSS avatar can be replaced by a GLB/VRM character rendered with Three.js without changing the interview engine.

## Security
- Password hashing
- Session authentication
- Role checks
- Creator permission checks
- Access-code authorization
- Interview ownership checks
- Duplicate submission protection
- Audit logging
- Server-side input validation
- Controlled error responses

## Testing checklist
- Master password login
- Creator password login
- Learner password login
- OTP login
- Forgot password
- Invalid access code
- Disabled access code
- Correct access code
- Self introduction present first
- Empty answer = 0
- Gibberish answer = 0
- Off-topic answer = 0 when no relevant concepts are detected
- Partial answer gets partial score
- Strong answer gets high score
- Duplicate submission rejected
- Camera permission failure handled
- Microphone permission failure handled
- Report generation
- Unauthorized creator/master URL access rejected

## Implementation strategy
The project was enhanced in-place from the existing NEXA v3 package. Existing Flask routes, templates, question generation and report logic are retained where practical, with the new access-code, OTP, permission, strict-validation and 3D UI layers added around them.
