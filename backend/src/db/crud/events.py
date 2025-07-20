from ..connection import SessionLocal
from ..models import Event
from datetime import datetime
from sqlalchemy import and_
from ...services import convert_timezone_to_local, convert_timezone_to_utc

def create_event(title: str, description: str, tags, importance_level: str = "",
                 last_notified_on=None, start_time=None, end_time=None, reminder_interval: int = 60*60*4):
    now = datetime.now()
    if last_notified_on is None:
        last_notified_on = convert_timezone_to_utc(now)
    if start_time is None:
        start_time = convert_timezone_to_utc(now)
    if end_time is None:
        end_time = convert_timezone_to_utc(now)

    db = SessionLocal()
    try:
        new_event = Event(
            title=title,
            start_time=start_time,
            description=description,
            tags=tags,
            last_notified_on=last_notified_on,
            end_time=end_time,
            importance_level=importance_level,
            reminder_interval=reminder_interval
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        print(f"✅ Created event: {new_event.title}")
        return new_event
    finally:
        db.close()

def get_upcoming_events():
    now = datetime.utcnow()
    db = SessionLocal()
    try:
        events = db.query(Event).filter(Event.start_time > now).order_by(Event.start_time).all()

        final_list = []
        for event in events:
            final_list.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": convert_timezone_to_local(event.start_time) if event.start_time else None,
                "end_time": convert_timezone_to_local(event.end_time) if event.end_time else None,
                "importance_level": event.importance_level,
                "last_notified_on": convert_timezone_to_local(event.last_notified_on) if event.last_notified_on else None,
                "reminder_interval": event.reminder_interval,
                "tags": event.tags,
            })

        return final_list
    finally:
        db.close()

def get_ongoing_events():
    now = datetime.utcnow()
    db = SessionLocal()
    try:
        events = db.query(Event).filter(
            and_(Event.start_time <= now, Event.end_time >= now)
        ).order_by(Event.end_time).all()
        
        final_list = []
        for event in events:
            final_list.append({
                "id": event.id,
                "title": event.title,
                "description": event.description,
                "start_time": convert_timezone_to_local(event.start_time) if event.start_time else None,
                "end_time": convert_timezone_to_local(event.end_time) if event.end_time else None,
                "importance_level": event.importance_level,
                "last_notified_on": convert_timezone_to_local(event.last_notified_on) if event.last_notified_on else None,
                "reminder_interval": event.reminder_interval,
                "tags": event.tags,
            })

        return final_list
    finally:
        db.close()

def update_event(event_id: int, **kwargs):
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            print(f"⚠️ Event ID {event_id} not found.")
            return None
        
        datetime_fields = {"start_time", "end_time", "last_notified_on"}
        # update fields
        for key, value in kwargs.items():
            if hasattr(event, key):
                if key in datetime_fields and isinstance(value, datetime):
                    setattr(event, key, convert_timezone_to_utc(value))
                else:
                    setattr(event, key, value)

        db.commit()
        db.refresh(event)
        print(f"✅ Updated event ID {event_id}")
        return event
    finally:
        db.close()

def delete_event(event_id: int):
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            print(f"⚠️ Event ID {event_id} not found.")
            return False
        db.delete(event)
        db.commit()
        print(f"🗑 Deleted event ID {event_id}")
        return True
    finally:
        db.close()
