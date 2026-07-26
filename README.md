# AI Career Assistant Platform

The **AI Career Assistant Platform** is a production-ready Django application designed to help students and professionals optimize their careers using artificial intelligence. It incorporates resume parsing, document Q&A (RAG), mock coding & behavioral interviews, job recommendations, and cover letter generation.

---

## Features

- **Authentication & Profiles**: User signup, login, profile custom avatars, skills list tracking, profile completeness meter.
- **AI Resume Analyzer**: Parses PDF/DOCX/TXT files, computes ATS score, keyword matches, and provides structured suggestions.
- **AI Document Chat (RAG)**: Chat with uploaded PDFs/Word files. Responses are grounded in the document and reference source paragraphs and pages using LangChain, FAISS, and Gemini.
- **AI Interview Assistant**: Select a role and practice 5 mock behavioral or technical questions. Answers are evaluated and scored out of 10 with direct AI critiques.
- **Job Portal & Recommendation Engine**: Search and browse jobs. Computes a matching compatibility score (%) comparing user profile skills to job requirements.
- **AI Cover Letter Generator**: Generates customized cover letters using AI, which can be downloaded as DOCX or plain text files.
- **REST APIs**: Full endpoints for auth, profile, dashboard, jobs, chat, and interviews built using Django REST Framework.
- **Modern UI**: Designed with Bootstrap 5, responsive sidebar layout, CSS glassmorphism, dynamic theme switching (Dark/Light mode), and Chart.js integrations.

---

## Project Structure

```
ai-career-assistant/
│
├── accounts/          # Registration, login, profiles, avatars
├── resume_analyzer/   # PDF text extraction, ATS review, cover letters
├── document_chat/     # FAISS vector store indexes, LangChain, chat UI
├── interview_ai/      # Technical and behavioral mock sessions
├── jobs/              # Jobs database, bookmarks, applications, trackers
├── ai_services/       # Gemini API caller, mock fallbacks, custom embeddings
├── dashboard/         # Main Professional charts, landing page controllers
├── templates/         # HTML views and global layouts (base.html)
├── static/            # Styling sheets (style.css), JS, media assets
├── media/             # Uploaded user avatars, resumes, documents
├── requirements.txt   # Packages checklist
└── README.md          # Guide & Reference documentation
```

---

## Installation & Local Run

### Prerequisites
- Python 3.10 or higher installed.

### Setup Steps
1. **Clone or locate project folder**:
   ```bash
   cd "f:/ALL PROJECT/New folder"
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\Activate.ps1
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Requirements**:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   GEMINI_API_KEY=your_gemini_api_key_here
   # DATABASE_URL=postgres://user:pass@host:port/dbname (optional, defaults to SQLite)
   ```

5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Seed DB & Run Dev Server**:
   ```bash
   python manage.py shell -c "exec(open('C:/Users/ABC/.gemini/antigravity/brain/5c04650a-2279-43eb-928c-e81ae16229ad/scratch/seed_db.py').read())"
   python manage.py runserver
   ```

---

## REST API Documentation

All endpoints return JSON responses. Authentication header: standard session or basic auth.

### 1. Accounts
- **Register**: `POST /accounts/api/register/` (payload: `username`, `email`, `password`, `first_name`, `last_name`)
- **Login**: `POST /accounts/api/login/` (payload: `username`, `password`)
- **Profile**: `GET` / `PUT` `/accounts/api/profile/` (multipart form fields for avatar, skills, location, preferred_role, bio)

### 2. Resume Analyzer
- **Analyze**: `POST /resume/api/analyze/` (multipart payload: `file`)
- **History**: `GET /resume/api/history/`
- **Cover Letter**: `POST /resume/api/cover-letter/` (payload: `company_name`, `job_description`)

### 3. Document Chat
- **Upload**: `POST /chat/api/upload/` (multipart payload: `file`)
- **History**: `GET /chat/api/messages/<doc_id>/`
- **Ask Question**: `POST /chat/api/ask/<doc_id>/` (payload: `message`)

### 4. Mock Interviews
- **Start**: `POST /interview/api/start/` (payload: `role`)
- **Submit Answer**: `POST /interview/api/submit/<question_id>/` (payload: `answer`)
- **Summary**: `GET /interview/api/session/<pk>/`

### 5. Jobs Portal
- **List/Search**: `GET /jobs/api/` (optional filters: `q`, `location`)
- **Apply**: `POST /jobs/api/apply/<job_id>/` (payload: `cover_letter`)
- **Bookmark**: `POST /jobs/api/bookmark/<job_id>/`
- **Tracker**: `GET /jobs/api/tracker/`

---

## Deployment Guide

### Backend (Render)
1. Link your GitHub repository to Render.
2. Select **Web Service** with runtime: **Python**.
3. Set Build Command:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
4. Set Start Command:
   ```bash
   gunicorn config.wsgi:application
   ```
5. Add Environment Variables: `SECRET_KEY`, `GEMINI_API_KEY`, `DATABASE_URL` (connecting to a PostgreSQL database).

### Media Storage
Configure `Cloudinary` or `AWS S3` for media assets upload if deploying on Render (since Render filesystem is ephemeral).
