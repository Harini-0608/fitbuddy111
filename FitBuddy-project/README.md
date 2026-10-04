# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite web application based on the supplied project specification. It generates a structured 7-day workout plan, a nutrition/recovery tip, and an AI-revised plan from feedback. It also includes API endpoints and an admin/coach view.

## Architecture

- Frontend: HTML, CSS, Jinja2 templates
- Backend: FastAPI
- AI: Google Gemini through the current `google-genai` Python SDK
- Database: SQLite + SQLAlchemy
- Server: Uvicorn
- Templates: `index.html`, `result.html`, `all_users.html`
- AI modules: `gemini_generator.py`, `updated_plan.py`

The PDF specifies Gemini 1.5 Pro and Gemini Flash. Those model names are treated as the original design roles; the project makes model names configurable because model availability changes over time.

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── gemini_generator.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   └── updated_plan.py
├── static/
│   └── style.css
├── templates/
│   ├── all_users.html
│   ├── index.html
│   └── result.html
├── tests/
│   └── test_app.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Windows / VS Code setup

1. Install Python 3.11+.
2. Open this `FitBuddy` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

```powershell
python -m venv venv
```

5. Activate it:

```powershell
venv\Scripts\activate
```

6. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

7. Create the environment file:

```powershell
copy .env.example .env
```

8. Open `.env` and put your Gemini API key after `GEMINI_API_KEY=`. The app also works without a key in demo/fallback mode.

9. Start the server:

```powershell
uvicorn app.main:app --reload
```

10. Open:

- Website: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Admin/coach view: http://127.0.0.1:8000/view-all-users
- Health check: http://127.0.0.1:8000/api/health

## Testing

With the virtual environment active:

```powershell
pytest -q
```

The tests use a temporary SQLite database and do not require a Gemini API key.

## Gemini configuration

The current Google Python SDK is `google-genai`. Set `GEMINI_API_KEY` in `.env`. If Google changes model availability, change `GEMINI_WORKOUT_MODEL` and `GEMINI_NUTRITION_MODEL` without changing application code.

## API examples

### Generate a plan

POST `/api/generate-workout`

```json
{
  "name": "Harini",
  "user_id": "FB001",
  "age": 18,
  "weight": 55,
  "goal": "general wellness",
  "intensity": "medium"
}
```

### Update a plan

POST `/api/submit-feedback`

```json
{
  "user_id": "FB001",
  "feedback": "Add more cardio and keep one additional recovery day."
}
```

## Notes for a production deployment

The supplied specification focuses on a local academic/demo deployment. Before public deployment, add real authentication, authorization, CSRF protection for HTML forms, HTTPS, secret management, database migrations, rate limiting, structured AI output validation, logging/monitoring, and stronger privacy controls.
