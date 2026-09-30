import json
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from auth import get_current_user
from planner_service import create_plan
from recommendations import generate_recommendations

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=50000000)
    event_type: str = Field(min_length=1, max_length=80)
    guests: int = Field(gt=0, le=10000)
    location: str = Field(default="Home", max_length=120)
    food_preference: str = Field(default="", max_length=120)
    includes: list[str] = Field(default_factory=list, max_length=8)
    notes: str = Field(default="", max_length=1000)

    @field_validator("event_type", "location", "food_preference", "notes", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value


def get_party_recommendations(budget, event_type, guests, location, food_preference, includes, notes):
    result, _ = generate_recommendations("party", {
        "budget": budget,
        "event_type": event_type,
        "guests": guests,
        "location": location,
        "food_preference": food_preference,
        "includes": includes or [],
        "notes": notes or "",
    })
    return json.dumps(result, ensure_ascii=False)

@router.get("/party-planner")
async def party_planner_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="party_planner.html")

@router.post("/generate-party")
async def generate_party(data: PartyRequest, user: dict = Depends(get_current_user)):
  payload = data.model_dump()
  preferences = {key: payload[key] for key in ("event_type", "guests", "location", "food_preference", "includes", "notes")}
  return create_plan(user, "party", payload, preferences)
