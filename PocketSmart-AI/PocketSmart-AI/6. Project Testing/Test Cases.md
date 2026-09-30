# Test Cases

Run the application from `5. Project Development Phase` with dependencies installed. AI-dependent cases require a valid Gemini API key and network access. Record actual results in `Test Results.md`.

| ID | Scenario | Steps / input | Expected result |
|---|---|---|---|
| TC-01 | Landing page | Open `/`. | Landing page renders without server error. |
| TC-02 | Planner navigation | Open `/home-planner`, `/party-planner`, `/jewelry-planner`. | Each planner page renders. |
| TC-03 | Home recommendation | Submit a positive budget, rooms, and style. | A home recommendation is returned and added to history. |
| TC-04 | Party recommendation | Submit event type, guest count, and budget. | A party plan is returned and added to history. |
| TC-05 | Jewelry recommendation | Submit occasion, budget, and preferences without image. | Suggestions are returned and added to history. |
| TC-06 | Jewelry image input | Submit a supported outfit image through the UI. | Request completes or returns a clear validation/service error. |
| TC-07 | History retrieval | Generate a plan, then request `/api/history`. | Response includes the generated entry and total count. |
| TC-08 | Clear history | DELETE `/api/history`, then GET it. | History is empty for the current server process. |
| TC-09 | Registration and login | Register a username, then request a token with its credentials. | Registration succeeds and valid credentials return a bearer token. |
| TC-10 | Duplicate registration | Register the same username twice. | Second request returns an appropriate client error. |
| TC-11 | Missing Gemini key | Start without `GEMINI_API_KEY`. | Startup fails with the configured explanatory error. |
| TC-12 | Gemini failure | Use invalid/unavailable API configuration and submit a plan. | Generation failure is reported; server remains available. |

Do not use real personal information or sensitive images for test evidence.
