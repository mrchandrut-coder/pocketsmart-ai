import base64
import binascii
import io
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, field_validator

from auth import get_current_user
from planner_service import create_plan
from recommendations import generate_recommendations

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=50000000)
    occasion: str = Field(min_length=1, max_length=100)
    jewelry_types: list[str] = Field(default_factory=list, max_length=8)
    metal_preference: str = Field(default="", max_length=80)
    platforms: list[str] = Field(default_factory=lambda: ["Amazon", "Flipkart", "Bluestone"], max_length=8)
    style_preferences: str = Field(default="", max_length=1000)
    image: str | None = Field(default=None, max_length=7000000)

    @field_validator("occasion", "metal_preference", "style_preferences", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value


def _decode_image(encoded_image: str | None) -> tuple[bytes | None, str | None]:
    if not encoded_image:
        return None, None
    try:
        image_data = base64.b64decode(encoded_image, validate=True)
        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Outfit image must be 5 MB or smaller")
        with Image.open(io.BytesIO(image_data)) as image:
            if image.width * image.height > 20000000:
                raise HTTPException(status_code=413, detail="Outfit image dimensions are too large")
            image_mime_type = Image.MIME.get(image.format)
            if image_mime_type not in {"image/jpeg", "image/png", "image/webp"}:
                raise HTTPException(status_code=415, detail="Use a JPEG, PNG, or WebP outfit image")
            image.verify()
        return image_data, image_mime_type
    except HTTPException:
        raise
    except (binascii.Error, UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="The outfit image is not a valid supported image") from exc


def get_jewelry_recommendations(budget, occasion, jewelry_types, metal_preference, platforms, style_preferences, image_b64):
    image_data, mime_type = _decode_image(image_b64)
    result, _ = generate_recommendations("jewelry", {
        "budget": budget,
        "occasion": occasion,
        "jewelry_types": jewelry_types or [],
        "metal_preference": metal_preference or "",
        "platforms": platforms or [],
        "style_preferences": style_preferences or "",
        "image": bool(image_data),
    }, image_data=image_data, image_mime_type=mime_type)
    return json.dumps(result, ensure_ascii=False)

@router.get("/jewelry-planner")
async def jewelry_planner_page(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request=request, name="jewelry_planner.html")

@router.post("/generate-jewelry")
async def generate_jewelry(data: JewelryRequest, user: dict = Depends(get_current_user)):
    image_data, mime_type = _decode_image(data.image)
    payload = data.model_dump(exclude={"image"})
    payload["image"] = bool(image_data)
    preferences = {key: payload[key] for key in ("occasion", "jewelry_types", "metal_preference", "platforms", "style_preferences")}
    return create_plan(user, "jewelry", payload, preferences, image_data, mime_type)
