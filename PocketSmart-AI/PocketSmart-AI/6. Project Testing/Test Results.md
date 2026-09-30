# Test Results

## Automated Run

| Date | Command | Environment | Result |
|---|---|---|---|
| 2026-09-29 | `python -m compileall -q "PocketSmart-AI/5. Project Development Phase" "PocketSmart-AI/6. Project Testing"` | Python 3.14.6, Windows | Passed |
| 2026-09-29 | `python -m pip check` | Installed `requirements.txt` environment | Passed; no broken requirements |
| 2026-09-29 | `python -m unittest discover -s "PocketSmart-AI/6. Project Testing" -p "test_*.py" -v` | FastAPI TestClient; isolated temporary SQLite; Gemini key absent | 8 tests passed |

Automated coverage includes all HTML/Jinja templates, public and protected routes, registration and duplicate/invalid registration, bcrypt/JWT login, cookie and bearer authentication, logout, all three offline planners, budget totals, per-user history isolation and clearing, valid/invalid outfit images, the empty-services party case, the Gemini provider contract with a mocked SDK response, automatic SQLite creation, favicon/static assets, and generic recommendation validation.

## Browser Run

| Check | Result |
|---|---|
| Register, sign in, dashboard, and page navigation | Passed |
| Submit Home, Party, and Jewelry plans with Gemini unconfigured | Passed; each displayed `Offline recommendation` |
| History list and clear action | Passed; all three plans appeared and cleared |
| Logout and protected API access afterward | Passed; `/api/me` returned 401 |
| Jewelry text-injection probe | Passed; markup rendered as text and no injected image element appeared |
| Mobile layout at 390px | Passed; all private pages fit within the viewport without horizontal overflow |
| `/favicon.ico` | Passed; redirects to the SVG asset |

## Limitations

No Gemini API key was configured, so no live request was sent to Google. The configured-provider branch was tested with a mocked SDK response; live provider credentials, quota, and external availability remain unverified. Starlette emits a non-blocking `httpx` TestClient deprecation warning in this environment.
