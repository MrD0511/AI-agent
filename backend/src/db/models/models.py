from sqlalchemy import Column, String, Integer, Text, DateTime, Date, ARRAY, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    importance_level = Column(String)
    last_notified_on = Column(DateTime)
    reminder_interval = Column(Integer, default=60*60*4)
    tags = Column(ARRAY(String))  # e.g., ['work', 'urgent']

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "importance_level": self.importance_level,
            "last_notified_on": self.last_notified_on.isoformat() if self.last_notified_on else None,
            "reminder_interval": self.reminder_interval,
            "tags": self.tags
        }

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    notification_message = Column(Text, nullable=False)
    reminder_time = Column(DateTime, nullable=False)
    is_notification_sent = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "notification_message": self.notification_message,
            "reminder_time": self.reminder_time.isoformat(),
            "is_notification_sent": self.is_notification_sent,
            "created_at": self.created_at.isoformat()
        }
