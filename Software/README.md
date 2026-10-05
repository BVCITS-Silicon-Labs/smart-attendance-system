# Face Attendance System

Local classroom face-recognition attendance system for students.

## Features
- Student registration with a profile photo
- Face embedding based recognition
- Laptop webcam live attendance
- Daily camera frames are processed in memory and never saved
- One attendance record per student per day
- Today's attendance dashboard
- CSV export
- HTTP authorization signal
- SQLite database
- Responsive local dashboard

## Run on Windows
1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Run:
   `python -m venv .venv`
4. Run:
   `.venv\Scripts\activate`
5. Run:
   `pip install -r backend\requirements.txt`
6. Copy `.env.example` to `.env` and edit  settings.
7. Run `start.bat`.
8. Open http://127.0.0.1:8000

The first InsightFace initialization can download the configured face model. That model is the main storage consumer.

IMPORTANT: biometric face data is sensitive. Keep the application local/private and follow applicable institutional/privacy requirements.
