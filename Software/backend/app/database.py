from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import settings, ROOT

url = settings.database_url
if url.startswith("sqlite:///./"):
    db_path = ROOT / url.replace("sqlite:///./", "")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{db_path}"

engine = create_engine(
    url,
    connect_args={"check_same_thread": False} if url.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
