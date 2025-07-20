from pytz import timezone
from zoneinfo import ZoneInfo
from datetime import datetime

def convert_timezone_to_utc(local_datetime: datetime, timezone_str: str = "Asia/Kolkata") -> datetime:
    """
    Converts a naive local datetime (e.g., from user input) to a UTC datetime,
    assuming the given timezone.
    """
    try:
        # Make the datetime timezone-aware
        local_dt = local_datetime.replace(tzinfo=ZoneInfo(timezone_str))
        
        # Convert to UTC
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        return utc_dt

    except Exception as e:
        print("convert_timezone_to_utc error:", e)
        return None

def convert_timezone_to_local(utc_datetime: datetime, timezone_str: str = "Asia/Kolkata") -> datetime:
    """Converts UTC time to local timezone"""
    try:
        local_dt = utc_datetime.astimezone(ZoneInfo(timezone_str))
        return local_dt
    except Exception as e:
        print("convert_utc_to_timezone error:", e)
        return None
