# ⚡ MindSnap — AI-Powered Visual Second Brain

MindSnap is a full-stack web application that lets you save anything — articles, URLs, code snippets, ideas — and uses AI to automatically analyze, summarize, and tag your content. Search everything later in plain English.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**🌐 Live Demo:** [mindsnap-sigma.vercel.app](https://mindsnap-sigma.vercel.app)
**📡 API Docs:** [mindsnap-production.up.railway.app/docs](https://mindsnap-production.up.railway.app/docs)

---

## 🚀 Features

- **AI Content Analysis** — Paste any text or URL and get an auto-generated title, summary, content type, and tags
- **Smart Fallback Chain** — Uses Gemini → Claude → Groq in order, automatically switching if one hits a quota limit
- **JWT Authentication** — Secure register/login with bcrypt password hashing
- **Keyword Search** — Search across all your saved snaps by title, summary, or tags
- **Full CRUD** — Create, view, search, and delete snaps
- **Clean Dashboard** — Minimal React UI built with Tailwind CSS

---

## 🏗️ Architecture

```
mindsnap/
├── backend/                  ← FastAPI (Python)
│   ├── app/
│   │   ├── main.py           ← App entry point, CORS, route registration
│   │   ├── database.py       ← SQLAlchemy + PostgreSQL connection
│   │   ├── models/
│   │   │   ├── user.py       ← Users table
│   │   │   └── snap.py       ← Snaps table
│   │   ├── routes/
│   │   │   ├── auth.py       ← /auth/register, /auth/login
│   │   │   └── snaps.py      ← /snaps CRUD + search
│   │   └── services/
│   │       ├── auth_service.py   ← JWT + bcrypt
│   │       └── ai_service.py     ← AI fallback chain
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 ← React + Vite
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   └── services/
│   │       ├── api.js        ← Axios instance with JWT interceptor
│   │       ├── auth.js       ← Login, register, logout helpers
│   │       └── snaps.js      ← Snap API calls
│   └── package.json
└── docker-compose.yml
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS, Axios |
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL (Railway) |
| Auth | JWT (python-jose), bcrypt (passlib) |
| ORM | SQLAlchemy |
| AI | Gemini API, Claude API, Groq API |
| DevOps | Docker, Railway, Vercel |

---

## ⚙️ How the AI Fallback Chain Works

MindSnap uses three AI providers in a priority order. If one fails or hits a quota limit, it automatically tries the next:

```
1. Gemini 2.0 Flash Lite  ← tried first (free tier)
        ↓ fails?
2. Claude Haiku           ← second attempt
        ↓ fails?
3. Groq (LLaMA 3.1)      ← final fallback (free tier)
```

This means MindSnap keeps working even when one API is down or rate limited.

---

## 📦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- At least one AI API key: [Gemini](https://aistudio.google.com), [Anthropic](https://console.anthropic.com), or [Groq](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/Chahethsen12/mindsnap.git
cd mindsnap
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-long-random-secret-key
GEMINI_API_KEY=AIzaSy...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...
```

> You only need at least ONE AI API key. The fallback chain handles the rest.

### 4. Run the backend
```bash
uvicorn app.main:app --reload
```

API is live at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

### 5. Set up the frontend
```bash
cd ../frontend
npm install
npm run dev
```

Frontend is live at `http://localhost:5173`

---

## 🐳 Run with Docker

```bash
docker-compose up
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create a new account | No |
| POST | `/auth/login` | Login, returns JWT token | No |
| POST | `/snaps/` | Create a new snap (AI analyzed) | Yes |
| GET | `/snaps/` | Get all your snaps | Yes |
| GET | `/snaps/search?q=` | Search snaps by keyword | Yes |
| DELETE | `/snaps/{id}` | Delete a snap | Yes |
| GET | `/health` | Health check | No |

### Example — Create a Snap
```bash
curl -X POST "https://mindsnap-production.up.railway.app/snaps/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"raw_text": "FastAPI is a modern web framework for building APIs with Python"}'
```

Response:
```json
{
  "id": 1,
  "title": "FastAPI: Modern Python Web Framework",
  "summary": "FastAPI is a high-performance web framework for building APIs...",
  "content_type": "tutorial",
  "source_url": null,
  "tags": "fastapi, python, api, backend, web"
}
```

---

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Snaps table
CREATE TABLE snaps (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR,
    summary TEXT,
    content_type VARCHAR,
    source_url VARCHAR,
    image_path VARCHAR,
    tags VARCHAR,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔮 Planned Features

- [ ] URL fetching — paste a link and auto-scrape the content
- [ ] Image/screenshot upload with vision AI analysis
- [ ] Semantic search using vector embeddings (pgvector)
- [ ] Collections and folders
- [ ] Chrome extension — right-click anything to snap it
- [ ] Export snaps as Markdown or PDF

---

## 👨‍💻 Author

**Chaheth Senevirathne**
- GitHub: [@Chahethsen12](https://github.com/Chahethsen12)
- LinkedIn: [chaheth-senevirathne](https://linkedin.com/in/chaheth-senevirathne)

---

## 📄 License

MIT License — feel free to use, modify and build on this project.