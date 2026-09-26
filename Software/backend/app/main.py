from datetime import datetime, date
import csv, io

import cv2
import numpy as np
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .database import Base, engine, get_db, SessionLocal
from .models import Student, Attendance
from .schemas import StudentOut, AttendanceOut
from .config import PHOTO_DIR, settings, ROOT
from .services.face_service import FaceService
from .services.esp32_service import health as device_health, set_led, get_last_color

Base.metadata.create_all(bind=engine)

face_service = FaceService()
app = FastAPI(title="Face Attendance + SiWG917 BRD2605A")
FRONTEND = ROOT / "frontend"
app.mount("/frontend", StaticFiles(directory=str(FRONTEND)), name="frontend")


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        face_service.load_cache(
            db.execute(
                select(Student).where(Student.is_active == True)
            ).scalars().all()
        )
    finally:
        db.close()

    # Normal idle state
    set_led("blue")


@app.get("/", response_class=HTMLResponse)
def home():
    return (FRONTEND / "index.html").read_text(encoding="utf-8")


def decode_image(data):
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Invalid image")
    return img


def save_small_photo(data, filename):
    if len(data) > settings.max_photo_mb * 1024 * 1024:
        raise HTTPException(413, "Photo is too large")

    img = decode_image(data)
    h, w = img.shape[:2]
    scale = min(1.0, 1024 / max(h, w))

    if scale < 1:
        img = cv2.resize(
            img,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA,
        )

    path = PHOTO_DIR / filename
    cv2.imwrite(
        str(path),
        img,
        [cv2.IMWRITE_JPEG_QUALITY, 82],
    )
    return str(path.relative_to(ROOT.parent)).replace("\\", "/")


@app.get("/api/students", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db)):
    return db.execute(
        select(Student).order_by(Student.name)
    ).scalars().all()


@app.post("/api/students", response_model=StudentOut)
async def add_student(
    student_id: str = Form(...),
    roll_number: str = Form(...),
    name: str = Form(...),
    class_name: str = Form(...),
    section: str = Form(...),
    department: str = Form(""),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if db.execute(
        select(Student).where(Student.student_id == student_id.strip())
    ).scalar_one_or_none():
        raise HTTPException(409, "Student ID already exists")

    data = await image.read()
    img = decode_image(data)

    try:
        emb = face_service.embedding_from_bgr(img)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=(
                "Face recognition model is unavailable. "
                "Install InsightFace / Visual C++ build tooling first."
            ),
        ) from e
    except ValueError as e:
        raise HTTPException(400, str(e))

    safe = "".join(
        c for c in student_id
        if c.isalnum() or c in "-_"
    )

    photo_path = save_small_photo(
        data,
        f"{safe}.jpg",
    )

    s = Student(
        student_id=student_id.strip(),
        roll_number=roll_number.strip(),
        name=name.strip(),
        class_name=class_name.strip(),
        section=section.strip(),
        department=department.strip(),
        photo_path=photo_path,
        face_embedding=face_service.serialize(emb),
        is_active=True,
    )

    db.add(s)
    db.commit()
    db.refresh(s)
    face_service.add_to_cache(s)

    return s


@app.post("/api/students/{student_pk}/deactivate")
def deactivate_student(
    student_pk: int,
    db: Session = Depends(get_db),
):
    s = db.get(Student, student_pk)

    if not s:
        raise HTTPException(404, "Student not found")

    s.is_active = False
    db.commit()
    face_service.remove_from_cache(s.id)

    return {"success": True}


@app.post("/api/recognition/recognize")
async def recognize(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    data = await image.read()
    img = decode_image(data)

    try:
        student_pk, score = face_service.recognize(
            img,
            settings.face_match_threshold,
        )

    except RuntimeError as e:
        set_led("blue")
        return {
            "recognized": False,
            "message": (
                "Face recognition model is unavailable. "
                "Install InsightFace / Visual C++ build tooling first."
            ),
            "led": {
                "color": "blue",
                "signal_sent": False,
            },
        }

    except ValueError as e:
        # FaceService uses this for no-face / multiple-face conditions.
        message = str(e)

        if "No face detected" in message:
            color = "blue"
        else:
            color = "blue"

        ok, detail = set_led(color)

        return {
            "recognized": False,
            "message": message,
            "led": {
                "color": color,
                "signal_sent": ok,
                "detail": detail,
            },
        }

    # Face detected but no registered match.
    if student_pk is None:
        ok, detail = set_led("red")

        return {
            "recognized": False,
            "message": "Unknown face",
            "confidence": score,
            "led": {
                "color": "red",
                "signal_sent": ok,
                "detail": detail,
            },
        }

    student = db.get(Student, student_pk)

    if not student or not student.is_active:
        ok, detail = set_led("red")

        return {
            "recognized": False,
            "message": "Inactive student",
            "led": {
                "color": "red",
                "signal_sent": ok,
                "detail": detail,
            },
        }

    # Correct registered person.
    ok, detail = set_led("green")

    now = datetime.now()

    existing = db.execute(
        select(Attendance).where(
            Attendance.student_id == student.id,
            Attendance.attendance_date == now.date(),
        )
    ).scalar_one_or_none()

    if existing:
        return {
            "recognized": True,
            "student": StudentOut.model_validate(student).model_dump(),
            "confidence": score,
            "attendance": {
                "status": "PRESENT",
                "already_present": True,
                "date": str(now.date()),
                "time": str(existing.attendance_time),
            },
            "led": {
                "color": "green",
                "signal_sent": ok,
                "detail": detail,
            },
        }

    a = Attendance(
        student_id=student.id,
        attendance_date=now.date(),
        attendance_time=now.time().replace(microsecond=0),
        status="PRESENT",
        confidence=score,
    )

    db.add(a)
    db.commit()

    return {
        "recognized": True,
        "student": StudentOut.model_validate(student).model_dump(),
        "confidence": score,
        "attendance": {
            "status": "PRESENT",
            "already_present": False,
            "date": str(now.date()),
            "time": str(a.attendance_time),
        },
        "led": {
            "color": "green",
            "signal_sent": ok,
            "detail": detail,
        },
    }


@app.get("/api/attendance/today", response_model=list[AttendanceOut])
def today(db: Session = Depends(get_db)):
    return db.execute(
        select(Attendance).where(
            Attendance.attendance_date == date.today()
        ).order_by(Attendance.attendance_time)
    ).scalars().all()


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total = db.scalar(
        select(func.count()).select_from(Student).where(
            Student.is_active == True
        )
    ) or 0

    present = db.scalar(
        select(func.count()).select_from(Attendance).where(
            Attendance.attendance_date == date.today()
        )
    ) or 0

    return {
        "total_students": total,
        "present": present,
        "absent": max(0, total - present),
        "percentage": round(100 * present / total, 1) if total else 0,
        "device_online": device_health(),
        "device_ip": settings.device_ip,
        "led_color": get_last_color(),
    }


@app.get("/api/device/status")
def device_status():
    return {
        "online": device_health(),
        "ip": settings.device_ip,
        "port": settings.device_port,
        "led_color": get_last_color(),
    }


@app.post("/api/device/led/{color}")
def device_led(color: str):
    ok, detail = set_led(color)
    return {
        "success": ok,
        "color": color,
        "detail": detail,
    }


@app.get("/api/esp32/status")
def legacy_esp32_status():
    return {
        "online": device_health(),
        "ip": settings.device_ip,
    }


@app.get("/api/reports/csv")
def csv_report(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Attendance).order_by(
            Attendance.attendance_date.desc(),
            Attendance.attendance_time.desc(),
        )
    ).scalars().all()

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow([
        "Date",
        "Time",
        "Student DB ID",
        "Status",
        "Confidence",
    ])

    for a in rows:
        w.writerow([
            a.attendance_date,
            a.attendance_time,
            a.student_id,
            a.status,
            f"{a.confidence:.4f}",
        ])

    return StreamingResponse(
        io.BytesIO(out.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=attendance.csv"
        },
    )
