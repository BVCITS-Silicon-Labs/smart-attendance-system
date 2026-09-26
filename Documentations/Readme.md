# Smart Face Attendance and Access Gate System

An AI + IoT based automated attendance and access-control system using
face recognition and the Silicon Labs SiWG917/BRD2605A development board.

## 🚀 Overview

The Smart Face Attendance and Access Gate System automates student attendance
using facial recognition and provides real-time hardware status indication
through a Silicon Labs SiWG917 IoT board.

The system captures a student's face using a webcam, generates a facial
embedding, compares it with registered student embeddings, and automatically
records attendance when a valid student is recognized.

The system also communicates with the SiWG917 over Wi-Fi. The board operates
as an HTTP server and controls an RGB LED according to the recognition status.

## ✨ Features

- 👤 Student registration with personal and academic details
- 📷 Webcam-based live face recognition
- 🧠 Facial embedding generation using InsightFace
- 🔍 Similarity-based face matching
- 📝 Automatic attendance recording
- ⏱️ Date, time, status and confidence tracking
- 🚫 Prevents duplicate attendance on the same day
- 🌐 FastAPI-based REST backend
- 📊 Web dashboard for attendance monitoring
- 📄 CSV attendance report generation
- 🗄️ SQLite database
- 📡 Wi-Fi communication with Silicon Labs SiWG917
- 💡 RGB LED status indication
- 🔐 API-key authentication for IoT commands
- ⚡ Local processing and database operation

## 🛠️ Technologies Used

### Software

- Python
- FastAPI
- OpenCV
- InsightFace
- ONNX Runtime
- NumPy
- SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript

### Hardware

- Silicon Labs SiWG917 / SiWx917
- BRD2605A Development Board
- Laptop / PC
- Webcam
- RGB LED
- USB cable
- Wi-Fi network

## 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │     Student      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     Webcam       │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │     Backend      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     OpenCV       │
                    │ Face Processing  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   InsightFace    │
                    │ Face Embedding   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Similarity Match │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  SQLite Database │
                    └────────┬─────────┘
                             │
                     Attendance Valid
                             │
                             ▼
                         Wi-Fi
                             │
                             ▼
                 ┌──────────────────────┐
                 │ Silicon Labs SiWG917 │
                 │      BRD2605A        │
                 └──────────┬───────────┘
                            │
                            ▼
                      ┌───────────┐
                      │ RGB LED   │
                      └───────────┘