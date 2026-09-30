import json
import uuid
from datetime import datetime, timezone
from typing import Any

from database import save_recommendation
from recommendations import generate_recommendations


def create_plan(
    user: dict[str, Any],
    category: str,
    data: dict[str, Any],
    preferences: dict[str, Any],
    image_data: bytes | None = None,
    image_mime_type: str | None = None,
) -> dict[str, Any]:
    result, source = generate_recommendations(
        category,
        data,
        image_data=image_data,
        image_mime_type=image_mime_type,
    )
    recommendation_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    save_recommendation(
        recommendation_id=recommendation_id,
        user_id=user["id"],
        category=category,
        budget=float(data["budget"]),
        preferences=preferences,
        result=json.dumps(result, ensure_ascii=False),
        timestamp=timestamp,
    )
    return {
        "recommendations": json.dumps(result, ensure_ascii=False),
        "budget": data["budget"],
        "id": recommendation_id,
        "source": source,
    }
