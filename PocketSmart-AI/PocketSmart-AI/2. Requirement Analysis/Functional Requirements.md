# Functional Requirements

| ID | Requirement | Current status |
|---|---|---|
| FR-01 | Display the landing page and navigation to application pages. | Implemented |
| FR-02 | Register a user and authenticate with username and password. | Basic API; in-memory only |
| FR-03 | Accept home budget, room, style, platform, and preference inputs. | Implemented |
| FR-04 | Generate a home recommendation plan through Gemini. | Implemented; requires API access |
| FR-05 | Accept party budget, event, guest, venue, food, and service inputs. | Implemented |
| FR-06 | Generate a party budget plan through Gemini. | Implemented; requires API access |
| FR-07 | Accept jewelry budget, occasion, type, metal, and style preferences. | Implemented |
| FR-08 | Optionally use an outfit image for jewelry suggestions. | Supported by request model |
| FR-09 | Store generated recommendations in history and expose history endpoints. | Implemented in process memory |
| FR-10 | Clear recommendation history. | Implemented; clears shared process state |
| FR-11 | Present planner and history views through HTML templates. | Implemented |

## Acceptance Notes

AI-generated output is unverified text. A production version should validate response shape, price totals, user ownership, and external URLs before presenting results as reliable.
