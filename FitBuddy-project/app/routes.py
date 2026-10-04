from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .schemas import UserInput, FeedbackRequest
from .database import save_user, save_plan, get_user, get_latest_plan, get_all_users, get_all_plans, update_plan, delete_user
from .gemini_generator import safe_generate_workout, safe_generate_tip
from .updated_plan import safe_update_plan
from .config import settings

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def page_context(request: Request, **kwargs):
    return {"request": request, **kwargs}

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context=page_context(request))

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    name: str = Form(...), user_id: str = Form(...), age: int = Form(...),
    weight: float = Form(...), goal: str = Form(...), intensity: str = Form(...)
):
    try:
        data = UserInput(name=name, user_id=user_id, age=age, weight=weight, goal=goal, intensity=intensity)
    except Exception as exc:
        return templates.TemplateResponse(request=request, name="index.html", context=page_context(request, error=str(exc)))
    workout = safe_generate_workout(data.name, data.age, data.weight, data.goal, data.intensity)
    tip = safe_generate_tip(data.goal)
    save_user(data.model_dump())
    save_plan(data.user_id, workout, tip)
    return templates.TemplateResponse(request=request, name="result.html", context=page_context(request, user=data.model_dump(), workout_plan=workout, nutrition_tip=tip, updated_plan=None, message=None))

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: str = Form(...), feedback: str = Form(...)):
    try:
        req = FeedbackRequest(user_id=user_id, feedback=feedback)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    user = get_user(req.user_id)
    plan = get_latest_plan(req.user_id)
    if not user or not plan:
        raise HTTPException(status_code=404, detail="User or workout plan not found")
    revised = safe_update_plan(plan.original_plan, req.feedback)
    update_plan(req.user_id, revised, req.feedback)
    user_data = {"name": user.name, "user_id": user.user_id, "age": user.age, "weight": user.weight, "goal": user.goal, "intensity": user.intensity}
    return templates.TemplateResponse(request=request, name="result.html", context=page_context(request, user=user_data, workout_plan=plan.original_plan, nutrition_tip=plan.nutrition_tip, updated_plan=revised, message="Your plan has been updated from your feedback."))

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    users = get_all_users()
    plans = get_all_plans()
    latest = {}
    for plan in plans:
        latest.setdefault(plan.user_id, plan)
    return templates.TemplateResponse(request=request, name="all_users.html", context=page_context(request, users=users, plans=latest))

@router.post("/admin/delete/{user_id}")
def admin_delete(user_id: str, password: str = Form(...)):
    if password != settings.admin_password:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    delete_user(user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)

@router.get("/api/health")
def health():
    return {"status": "ok", "service": "FitBuddy"}

@router.post("/api/generate-workout")
def api_generate(payload: UserInput):
    workout = safe_generate_workout(payload.name, payload.age, payload.weight, payload.goal, payload.intensity)
    tip = safe_generate_tip(payload.goal)
    save_user(payload.model_dump()); plan = save_plan(payload.user_id, workout, tip)
    return {"user_id": payload.user_id, "plan_id": plan.id, "workout_plan": workout, "nutrition_tip": tip}

@router.post("/api/submit-feedback")
def api_feedback(payload: FeedbackRequest):
    plan = get_latest_plan(payload.user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    revised = safe_update_plan(plan.original_plan, payload.feedback)
    update_plan(payload.user_id, revised, payload.feedback)
    return {"user_id": payload.user_id, "updated_plan": revised}
