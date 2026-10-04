try:
    from google import genai
    from google.genai import types
except ImportError:  # Optional at runtime when demo fallback mode is used.
    genai = None
    types = None
from .config import settings

SYSTEM = """You are FitBuddy, a careful fitness-planning assistant. Create practical general wellness guidance, not diagnosis or medical treatment. Never encourage dangerous restriction, overtraining, or exercise through significant pain. Keep plans realistic and include rest/recovery."""

def _client():
    if not settings.gemini_api_key or genai is None:
        return None
    return genai.Client(api_key=settings.gemini_api_key)

def _generate(model: str, prompt: str, max_tokens: int = 1800) -> str:
    client = _client()
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0.65,
            max_output_tokens=max_tokens,
        ),
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text.strip()

def generate_workout_gemini(name: str, age: int, weight: float, goal: str, intensity: str) -> str:
    prompt = f"""Create a personalized 7-day workout plan for:
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

Use exactly seven day headings. For each day include Focus, Warm-up (5–10 min), Main Workout (exercise + sets/reps or duration), and Cooldown/Recovery. Include at least one recovery/rest-oriented day. Keep it beginner-friendly unless the intensity says otherwise. Do not claim the plan is medically individualized."""
    return _generate(settings.workout_model, prompt)

def generate_nutrition_tip_with_flash(goal: str) -> str:
    prompt = f"Give one concise, practical nutrition or recovery tip for someone whose fitness goal is {goal}. Mention one concrete example. Keep it under 100 words and avoid prescriptive medical claims."
    return _generate(settings.nutrition_model, prompt, 400)

def fallback_workout(name: str, goal: str, intensity: str) -> str:
    scale = {"low": "2 sets", "medium": "3 sets", "high": "3–4 sets"}[intensity]
    focus = "fat-loss friendly full-body conditioning" if goal == "weight loss" else "strength and muscle-building" if goal == "muscle gain" else "balanced full-body wellness"
    return f"""FITBUDDY DEMO PLAN — {name}\n\nDay 1 — Full Body\nFocus: {focus}\nWarm-up: 5–10 min brisk walking + mobility\nMain: Squats {scale} × 10–12; Incline push-ups {scale} × 8–12; Glute bridges {scale} × 12; Plank 3 × 20–40 sec\nCooldown: 5 min easy walking and stretching\n\nDay 2 — Cardio\nWarm-up: 5 min easy walk\nMain: 20–30 min brisk walking/cycling; finish with 3 × 30 sec faster intervals\nCooldown: 5 min easy pace\n\nDay 3 — Upper Body + Core\nWarm-up: arm circles + light cardio\nMain: Rows {scale} × 10–12; Shoulder press {scale} × 8–12; Dead bug 3 × 8/side; Side plank 2 × 20 sec/side\nCooldown: upper-body stretches\n\nDay 4 — Recovery\n20–30 min easy walk + gentle mobility. Keep effort comfortable.\n\nDay 5 — Lower Body\nWarm-up: 5–10 min walking + hip mobility\nMain: Squats {scale} × 10; Reverse lunges {scale} × 8/side; Hip hinge {scale} × 10; Calf raises 3 × 12–15\nCooldown: gentle leg stretches\n\nDay 6 — Cardio + Core\nWarm-up: 5 min easy pace\nMain: 20 min moderate cardio; Bird dog 3 × 8/side; Plank 3 × 20–40 sec\nCooldown: 5 min easy pace\n\nDay 7 — Rest / Light Movement\nEasy walking, stretching, hydration and sleep focus.\n\nNote: This is general fitness information. Stop if you feel significant pain, dizziness, chest pain, or unusual shortness of breath and seek appropriate professional help."""

def safe_generate_workout(*args, **kwargs) -> str:
    try:
        return generate_workout_gemini(*args, **kwargs)
    except Exception:
        if settings.allow_ai_fallback:
            return fallback_workout(args[0], args[3], args[4])
        raise

def safe_generate_tip(goal: str) -> str:
    try:
        return generate_nutrition_tip_with_flash(goal)
    except Exception:
        if settings.allow_ai_fallback:
            examples = {
                "muscle gain": "Include a protein-rich food in each main meal, such as eggs, fish, chicken, beans, paneer, or Greek yogurt, and stay hydrated.",
                "weight loss": "Build meals around vegetables, a protein source, whole-food carbohydrates, and a reasonable portion size rather than relying on extreme restriction.",
                "flexibility": "Pair regular mobility work with adequate hydration and balanced meals that provide protein and micronutrients.",
                "general wellness": "Prioritize regular meals, enough fluids, a variety of whole foods, and consistent sleep to support training and recovery.",
            }
            return examples.get(goal, examples["general wellness"])
        raise
