# Proposed Solution

Build a browser-based planning assistant with three guided workflows: home interiors, parties, and jewelry. Each workflow collects a budget and relevant preferences, sends a structured prompt to Google Gemini, and presents the generated recommendations in the web interface.

## User Flow

1. Open the app and choose a planner.
2. Enter a budget and category-specific preferences.
3. Generate a plan using the Gemini API.
4. Review the returned suggestions and revisit recent recommendations in History.

The application uses FastAPI routes, Jinja2 templates, and shared in-memory state. Future iterations should add persistent storage, stronger account isolation, and automated validation of AI output and budget totals.
