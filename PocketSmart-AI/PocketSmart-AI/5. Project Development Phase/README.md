# PocketSmart AI — Development Guide

PocketSmart AI is a **FastAPI** budget-planning app for home interiors, parties, and jewelry. Gemini recommendations are optional; without a configured key or when the service is unavailable, the app returns structured offline plans. Accounts and recommendation history are stored in SQLite.

---

## ✨ Features

- 🏠 **Home Interior Planner** — Create room, style, and budget-based recommendations and shopping searches
- 🎉 **Party Budget Planner** — Plan events with smart cost splits across catering, decoration, entertainment, venue, photography, and gifts
- 💍 **Jewelry Planner** — Get occasion-based jewelry recommendations; Gemini can analyze outfit images when configured
- 📜 **Recommendation History** — View and clear account-specific plans stored in SQLite
- 🔐 **User Authentication** — SQLite-backed registration, bcrypt hashes, JWTs, and HttpOnly browser cookies
- 📊 **Dashboard** — Central hub to access all planners

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Recommendations | Google Gemini when configured; offline fallback otherwise |
| Frontend | Jinja2 Templates, HTML/CSS/JS |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Image Processing | Pillow |
| Storage | SQLite |

---

## 📁 Project Structure

```
5. Project Development Phase/
├── app.py                  # FastAPI app and shared routes
├── auth.py                 # Password hashing and JWT verification
├── database.py             # SQLite schema and persistence
├── models.py               # Pydantic request/user models
├── planner_service.py      # Shared plan creation and persistence
├── recommendations.py      # Gemini provider and offline fallback
├── routers/                # Auth, home, party, jewelry routes
├── templates/              # Jinja2 pages and inline browser scripts
├── static/                 # Static CSS
├── requirements.txt
└── .env.example
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/PocketSmart-AI-Your-Smart-Budget-Recommendation-Assistant.git
cd PocketSmart-AI-Your-Smart-Budget-Recommendation-Assistant
cd "5. Project Development Phase"
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
# macOS/Linux: source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the example file to `.env` in this directory:

```powershell
Copy-Item .env.example .env
```

`GEMINI_API_KEY` is optional; set it from [Google AI Studio](https://aistudio.google.com/) to enable Gemini, or leave it blank to use offline recommendations. A blank `SECRET_KEY` is generated at startup for local development; set a stable random value to keep sessions valid across restarts.

### 5. Run the application

```bash
uvicorn app:app --reload
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 🛒 Supported Shopping Platforms

| Category | Platforms |
|----------|-----------|
| Home & Decor | Amazon, Flipkart, IKEA, Meesho |
| Food & Catering | Swiggy, Zomato, Sulekha, JustDial |
| Venue | Google Maps, OYO, Booking.com, Sulekha |
| Photography / Entertainment | Sulekha, JustDial |
| Gifts & Decoration | Amazon, Flipkart, Meesho |

---


## 📦 Requirements

google-genai
Install all app and test dependencies from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Run the integration suite from the repository root:

```powershell
python -m unittest discover -s "6. Project Testing" -p "test_*.py" -v
```

---

## 🔒 Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `SECRET_KEY` | Secret key for JWT token signing |

Never commit `.env`; the repository-root `.gitignore` excludes it and local SQLite files.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---
## Demo Link

https://drive.google.com/file/d/1xzyRepwGcTW3uf0zOxxIdIfaH2ytCTTD/view?usp=drivesdk

---
## Documentation Link

https://docs.google.com/document/d/12o8cqba17NWcrYQJfg3Co6nMpTec1AgD/edit?usp=drivesdk&ouid=105926425446233546991&rtpof=true&sd=true
---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  Built with ❤️ using FastAPI & Google Gemini AI
</div>
