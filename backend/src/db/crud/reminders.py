from ..connection import SessionLocal
from ..models.models import Reminder
from datetime import datetime
from ...services import convert_timezone_to_local, convert_timezone_to_utc


def create_reminder(title: str, notification_message: str, reminder_time: datetime):
    reminder_time_utc = convert_timezone_to_utc(reminder_time)
    db = SessionLocal()
    """creates an reminder"""
    try:
        reminder = Reminder(
            title=title,
            notification_message=notification_message,
            reminder_time=reminder_time_utc,
            is_notification_sent=False
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        print(f"✅ Created event: {reminder.title} with id {reminder.id}")
        return reminder
    except Exception as e:
        print(f"[create_reminder] ❌ Exception: {e}")
        return None
    finally:
        db.close()


def get_upcoming_reminders():
    """returns upcoming reminders"""
    db = SessionLocal()
    try:
        now_utc = datetime.utcnow()
        reminders = db.query(Reminder).filter(Reminder.reminder_time >= now_utc).all()
        final_list = [
            {
                "id": reminder.id,
                "title": reminder.title,
                "notification_message": reminder.notification_message,
                "reminder_time": convert_timezone_to_local(reminder.reminder_time) if reminder.reminder_time else None,
                "is_notification_sent": reminder.is_notification_sent,
                "created_at": convert_timezone_to_local(reminder.created_at) if reminder.created_at else None
            }
            for reminder in reminders
        ]
        return final_list
    except Exception as e:
        print(f"[get_upcoming_reminders] ❌ Exception: {e}")
        return {"reminders": []}
    finally:
        db.close()


def update_reminder(reminder_id: int, title: str = None, notification_message: str = None, reminder_time: datetime = None):
    db = SessionLocal()
    try:
        reminder = db.query(Reminder).filter_by(id=reminder_id).first()
        if not reminder:
            print(f"[update_reminder] Reminder with id {reminder_id} not found.")
            return None

        if title is not None:
            reminder.title = title
        if notification_message is not None:
            reminder.notification_message = notification_message
        if reminder_time is not None:
            reminder.reminder_time = convert_timezone_to_utc(reminder_time)

        db.commit()
        db.refresh(reminder)
        return reminder
    except Exception as e:
        print(f"[update_reminder] ❌ Exception: {e}")
        return None
    finally:
        db.close()


def delete_reminder(reminder_id: int):
    db = SessionLocal()
    try:
        reminder = db.query(Reminder).filter_by(id=reminder_id).first()
        if not reminder:
            print(f"[delete_reminder] Reminder with id {reminder_id} not found.")
            return False

        db.delete(reminder)
        db.commit()
        print(f"🗑️ Deleted reminder id {reminder.id}")
        return True
    except Exception as e:
        print(f"[delete_reminder] ❌ Exception: {e}")
        return False
    finally:
        db.close()
