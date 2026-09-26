from datetime import date, datetime, time
from sqlalchemy import String, Integer, Date, Time, Float, Boolean, LargeBinary, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    roll_number: Mapped[str] = mapped_column(String(50), index=True)
    name: Mapped[str] = mapped_column(String(150))
    class_name: Mapped[str] = mapped_column(String(100))
    section: Mapped[str] = mapped_column(String(50))
    department: Mapped[str] = mapped_column(String(100), default="")
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    face_embedding: Mapped[bytes] = mapped_column(LargeBinary)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (UniqueConstraint("student_id", "attendance_date", name="uq_student_day"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, index=True)
    attendance_date: Mapped[date] = mapped_column(Date, index=True)
    attendance_time: Mapped[time] = mapped_column(Time)
    status: Mapped[str] = mapped_column(String(20), default="PRESENT")
    confidence: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
