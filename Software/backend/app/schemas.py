from datetime import date, time
from pydantic import BaseModel, ConfigDict

class StudentOut(BaseModel):
    id: int
    student_id: str
    roll_number: str
    name: str
    class_name: str
    section: str
    department: str
    photo_path: str | None
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class AttendanceOut(BaseModel):
    id: int
    student_id: int
    attendance_date: date
    attendance_time: time
    status: str
    confidence: float
    model_config = ConfigDict(from_attributes=True)
