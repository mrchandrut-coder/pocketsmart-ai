# Non-Functional Requirements

- **Usability:** Forms should use clear labels, input constraints, and actionable error messages.
- **Performance:** Non-AI pages should respond without waiting on external services; AI latency depends on Gemini.
- **Reliability:** External API errors should be reported without crashing the server.
- **Security:** Secrets must come from environment variables. Authentication, authorization, CORS, and data handling require hardening before production use.
- **Privacy:** Uploaded outfit images and preferences should be handled only for the requested recommendation and not retained without consent.
- **Maintainability:** Keep route handlers separated by feature and dependencies listed in `requirements.txt`.
- **Portability:** Support standard Python environments on Windows, macOS, and Linux.
- **Data durability:** Not currently met; users and history are held in memory and lost on restart.
