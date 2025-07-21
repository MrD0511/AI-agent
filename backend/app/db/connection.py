from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url, 
    echo=False,             # Disable SQL query logging for performance
    pool_size=10,           # Keep 10 connections in pool
    max_overflow=20,        # Allow up to 20 overflow connections
    pool_pre_ping=True,     # Validate connections before use
    pool_recycle=3600       # Recycle connections every hour
)

# Use scoped_session for thread-safe session management
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

@contextmanager
def get_db_session():
    """Context manager for database sessions with automatic cleanup"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()