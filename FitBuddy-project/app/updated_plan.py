from .gemini_generator import _generate
from .config import settings

def update_workout_plan(original_plan: str, feedback: str) -> str:
    prompt = f"""Revise the following FitBuddy 7-day workout plan according to the user's feedback.

ORIGINAL PLAN:
{original_plan}

USER FEEDBACK:
{feedback}

Return a complete revised seven-day plan, not just a list of changes. Preserve useful structure while applying the feedback. Include warm-up, main workout, and cooldown/recovery where appropriate, and keep at least one recovery/rest-oriented day. Do not provide medical diagnosis or unsafe recommendations."""
    return _generate(settings.workout_model, prompt, 2000)

def safe_update_plan(original_plan: str, feedback: str) -> str:
    try:
        return update_workout_plan(original_plan, feedback)
    except Exception:
        # A deterministic fallback makes local testing possible without an API key.
        return original_plan + f"\n\nUPDATED USING FEEDBACK (demo mode):\n{feedback}\n\nReview the schedule and adjust intensity conservatively."
