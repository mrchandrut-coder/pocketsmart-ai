# Project Overview

PocketSmart AI is a web-based assistant for planning expenses in three areas: home interiors, parties, and jewelry. Users provide a budget and preferences; the application asks Google Gemini to generate a recommendation and presents it through a browser interface.

## Components

- FastAPI provides page and API routes.
- Jinja2 templates and static CSS provide the web interface.
- Feature routers contain home, party, jewelry, and authentication handlers.
- Gemini generates recommendation text.
- A Python list stores recommendation history for the lifetime of the server process.

This is a demonstration application. Generated prices are estimates, and authentication and persistence are not production-ready.
