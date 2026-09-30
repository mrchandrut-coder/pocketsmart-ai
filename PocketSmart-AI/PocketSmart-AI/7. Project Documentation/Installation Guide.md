# Installation Guide

## Prerequisites

- Python 3.10 or newer and pip.
- A Google Gemini API key.
- Internet access to install packages and call Gemini.

## Windows PowerShell

From the repository root:

```powershell
Set-Location "5. Project Development Phase"
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY`. Set `SECRET_KEY` to a long, random value. Do not commit `.env` or share its values.

## Start the Server

```powershell
uvicorn app:app --reload
```

Browse to `http://127.0.0.1:8000`. Stop the development server with Ctrl+C.

## Troubleshooting

- A startup error about `GEMINI_API_KEY` means the variable is missing or `.env` is not being loaded from the development directory.
- AI generation requires network access and a valid Gemini API key with available quota.
- Activate the virtual environment before installing dependencies or starting the server.
