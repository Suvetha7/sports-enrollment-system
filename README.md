# Data-Driven Sports Enrollment and Management System

This project is a final-year Computer Science style web application built on sports enrollment analytics. It provides a sports program portal with registration, secure login, real-time seat tracking, duplicate prevention, transactional enrollment handling, and analytics dashboards.

The implementation is intentionally GitHub-friendly:

- clean modular Python backend
- responsive frontend with a polished dashboard
- SQLite demo database for easy local execution
- MySQL-ready schema and analytics queries in `sql/`
- project documentation for viva, report writing, and repository presentation

## Features

- Student registration with unique email and student ID validation
- Secure password hashing using PBKDF2
- Login verification
- Real-time seat availability for each sports program
- Atomic enrollment transaction to avoid overbooking
- Duplicate enrollment prevention
- Dashboard metrics for users, programs, enrollments, and occupancy
- Analytics by category and program utilization
- Recent activity feed

## Tech Stack

- Backend: Python standard library (`http.server`, `sqlite3`, `hashlib`, `json`)
- Database for demo: SQLite
- Database for deployment/report alignment: MySQL-compatible schema included
- Frontend: HTML, CSS, vanilla JavaScript

## Project Structure

```text
sports-enrollment-system/
├── data/
├── docs/
├── sql/
├── src/
├── static/
├── tests/
├── README.md
├── requirements.txt
└── run.py
```

## How to Run

1. Open a terminal in the project folder.
2. Run:

```bash
python3 run.py
```

3. Visit:

```text
http://127.0.0.1:8080
```

The app automatically creates `data/sports_analytics.db` and seeds demo records on first run.

## Demo Credentials

You can log in with either of these seeded accounts:

- `ananya.iyer@college.edu` / `Sports@123`
- `rahul.menon@college.edu` / `Sports@123`

## GitHub Push Steps

```bash
git init
git add .
git commit -m "Initial commit - sports enrollment system"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Final-Year Project Positioning

This repository is designed to look like a serious academic submission:

- problem-driven application design
- transaction-safe database operations
- analytics-oriented data model
- documented architecture and SQL layer
- extensible future scope for forecasting and recommendation systems

## Future Enhancements

- migrate from SQLite demo mode to MySQL deployment mode
- add role-based admin and coach dashboards
- build predictive enrollment forecasting
- send email notifications and waitlists
- integrate chart export and report generation

