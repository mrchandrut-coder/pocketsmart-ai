# Bug Fixes

| ID | Date | Reproduced issue | Fix | Verification |
|---|---|---|---|---|
| BF-01 | 2026-09-29 | App startup required a Gemini key; feature routers created clients during import. | Made Gemini optional and added structured offline plans. | No-key startup and all three planner tests pass. |
| BF-02 | 2026-09-29 | Accounts and history were in memory; history was shared across users. | Added SQLite users/recommendations with per-user queries and foreign keys. | Persistence, clearing, and account-isolation tests pass. |
| BF-03 | 2026-09-29 | Browser login stored a bearer token in localStorage while logout cleared only a cookie. | Login now sets an HttpOnly cookie; pages use cookie auth; logout clears it. | Browser registration/login/logout and API auth tests pass. |
| BF-04 | 2026-09-29 | AI-controlled recommendation strings were interpolated into HTML. | Escape generated fields and fallback text before rendering. | Browser injection probe showed literal text and no injected element. |
| BF-05 | 2026-09-29 | Party fallback left budget unallocated when all service options were deselected. | Added a flexible-needs category and retained the contingency allocation. | Dedicated full-budget regression test passes. |
| BF-06 | 2026-09-29 | At 390px, private-page navigation expanded the document to 844px. | Let nav items wrap on narrow viewports. | Browser measurements show no horizontal overflow at 390px. |
| BF-07 | 2026-09-29 | Browser favicon request returned 404. | Added a real SVG icon and `/favicon.ico` redirect. | Redirect and static asset tests pass. |
| BF-08 | 2026-09-29 | Bcrypt silently treated password suffixes past 72 bytes as equivalent. | Reject passwords exceeding bcrypt's UTF-8 byte limit. | 72-byte password accepted; 73-byte password returns validation error. |
