# Roadmap Gen

Roadmap Gen is an AI-powered college planning website built to help students navigate the college application process with more clarity and confidence. Instead of making students piece together advice from scattered sources, the app brings personalized roadmaps, essay feedback, and scholarship discovery into one place.

The goal is simple: give students a practical, supportive system for planning their academic path, improving their essays, and staying organized throughout the admissions journey.

## What The App Does

Roadmap Gen helps students:

- Generate personalized college planning roadmaps based on grade level, GPA, interests, activities, testing, and goals
- Receive AI-powered essay feedback with structured scoring and actionable revision advice
- Explore scholarships through a searchable and filterable scholarship experience
- Save roadmaps and essay results to a personal dashboard
- Sign in securely and access their data across sessions

## Why It Exists

Applying to college can feel overwhelming, especially for students who do not have easy access to mentors, counselors, or structured planning tools. Roadmap Gen is designed to make that process feel more accessible by combining guidance, organization, and feedback into a single product experience.

Rather than acting like a generic chatbot, the application aims to produce concrete next steps students can actually use.

## Core Experience

The website is centered around three main workflows:

### 1. Personalized Roadmaps

Students enter background information such as academic performance, extracurriculars, testing, interests, and college goals. The platform then generates a structured roadmap with:

- a personalized summary
- college list suggestions
- academic recommendations
- extracurricular suggestions
- a time-based action plan

### 2. Essay Feedback

Students can paste in a college essay and receive AI-generated feedback that scores the writing across multiple dimensions and returns specific improvement guidance.

### 3. Scholarship Discovery

Students can browse scholarship opportunities, filter them, and explore relevant funding options from within the same platform.

## Product Highlights

- Full-stack application with a dedicated frontend and backend
- Secure authentication and persistent user data
- AI-generated outputs stored to user accounts for later review
- Dashboard experience for revisiting roadmaps and essays
- Designed around college readiness, not just generic AI output

## Tech Stack

### Frontend

- React
- Vite
- Tailwind CSS
- Supabase Auth

### Backend

- FastAPI
- Groq API
- Supabase
- PostgreSQL

## Architecture Overview

The application is split into a React frontend and a FastAPI backend.

- The frontend handles the user experience, forms, routing, authentication state, and dashboard views
- The backend handles authenticated API requests, AI prompt orchestration, rate limiting, and persistence
- Supabase manages authentication and database storage
- Groq powers essay feedback and roadmap generation

The backend is organized into:

- `routers` for API endpoints
- `schemas` for request and response models
- `services` for AI and business logic
- `repositories` for database access
- `core` and `dependencies` for shared config, clients, and auth

## Current Feature Set

- User authentication with Supabase
- Personalized roadmap generation
- AI essay scoring and feedback
- Saved roadmaps and essays dashboard
- Scholarship browsing and filtering
- Rate-limited AI endpoints

## Future Direction

The project can grow into a much stronger student platform over time through:

- improved prompt evaluation and model quality testing
- analytics on roadmap and essay usage
- smarter scholarship ingestion pipelines
- background jobs for async AI and data workflows
- stronger personalization and progress tracking
- admin and moderation tools

## Running The Project

If you want to run the project locally:

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing During Development

If Supabase auth is getting in the way while you build, the project now supports a local dev session when:

- `frontend/.env` has `VITE_DEV_MODE=true`
- `backend/.env` has `DEV_MODE=true`

In that mode:

- the frontend creates a local test user so protected routes stay accessible
- the frontend sends the `dev-token-bypass` bearer token
- the backend accepts that token and treats the request as a dev user

This is meant for local development only. Keep it off in production.

### Backend Test Command

You can run the backend route tests without logging into Supabase:

```bash
cd backend
./venv/bin/python -m unittest discover -s tests -v
```

The starter tests show the pattern for bypassing auth cleanly with FastAPI dependency overrides.

## Environment Variables

### Backend

- `GROQ_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `DEV_MODE` optional
- `CORS_ORIGINS` optional

### Frontend

- `VITE_BACKEND`
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_DEV_MODE` optional

## Project Status

Roadmap Gen is actively evolving from a hackathon-style project into a more production-ready platform with stronger backend structure, cleaner API boundaries, and room for richer student-facing features.
