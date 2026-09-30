from contextlib import asynccontextmanager
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth import get_current_user
from database import clear_recommendations, initialize_database, list_recommendations
from planner_service import create_plan
from routers import auth, home, jewelry, party

PROJECT_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(PROJECT_DIR / "templates"))


@asynccontextmanager
async def lifespan(application: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="PocketSmart: AI Budget Planner", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(PROJECT_DIR / "static")), name="static")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/favicon.svg")


class RecommendationDetailsRequest(BaseModel):
    category: Literal["home", "party", "jewelry"] = "home"
    budget: float = Field(gt=0, le=50000000)
    preferences: dict[str, Any] = Field(default_factory=dict)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")


@app.get("/dashboard")
async def dashboard(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"username": user["username"]})


@app.get("/history")
async def history_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="history.html", context={"username": user["username"]})


@app.get("/startup")
async def startup_status():
    return {
        "status": "running",
        "message": "PocketSmart AI is operational",
        "ai_enabled": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/me")
async def current_user(user: dict = Depends(get_current_user)):
    return {"username": user["username"], "full_name": user["full_name"]}


@app.get("/api/history")
async def get_history_api(user: dict = Depends(get_current_user)):
    history = list_recommendations(user["id"])
    return {"total": len(history), "history": history}


@app.delete("/api/history")
async def clear_history_api(user: dict = Depends(get_current_user)):
    deleted = clear_recommendations(user["id"])
    return {"message": "History cleared successfully", "deleted": deleted}


@app.post("/recommendations-details")
async def recommendations_details(
    data: RecommendationDetailsRequest,
    user: dict = Depends(get_current_user),
):
    payload = {**data.preferences, "budget": data.budget}
    return create_plan(user, data.category, payload, data.preferences)


app.include_router(auth.router)
app.include_router(home.router)
app.include_router(party.router)
app.include_router(jewelry.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)