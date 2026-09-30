# Module Planning

| Module | Location | Responsibility |
|---|---|---|
| Application setup and page routes | `5. Project Development Phase/app.py` | Configure FastAPI, templates, static files, and shared endpoints. |
| Authentication helpers | `5. Project Development Phase/auth.py` | Password hashing, user lookup, authentication, and JWT creation. |
| Authentication routes | `5. Project Development Phase/routers/auth.py` | Registration, login, and logout endpoints. |
| Home planner | `5. Project Development Phase/routers/home.py` | Accept home-plan inputs and request Gemini recommendations. |
| Party planner | `5. Project Development Phase/routers/party.py` | Build event budget requests and history entries. |
| Jewelry planner | `5. Project Development Phase/routers/jewelry.py` | Build jewelry suggestions, including optional outfit image input. |
| Shared models and state | `models.py`, `state.py` | Pydantic user/token models and in-memory history. |
| User interface | `templates/`, `static/` | HTML views, browser behavior, and styling. |
