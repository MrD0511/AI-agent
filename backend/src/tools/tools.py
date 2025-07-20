import requests
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from ..gmail_auth import authenticate_gmail
import base64
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime
from typing import Literal, List
from ..db.crud.events import create_event, get_upcoming_events, get_ongoing_events
from ..db.crud.reminders import create_reminder, get_upcoming_reminders


WEATHERSTACK_API_KEY = "be23673cd6f87cc2dccf313a17854817"
WEATHERSTACK_URL = "http://api.weatherstack.com/current"

class Weather:
    def __init__(self, city: str):
        self.city = city
        self.params = {
            "access_key": WEATHERSTACK_API_KEY,
            "query": city
        }

    def get_weather(self) -> dict[str, any] | str:
        try:
            response = requests.get(WEATHERSTACK_URL, self.params)
            data = response.json()

            if "error" in data:
                return f"Error: {data['error']['info']}"

            return data
        except requests.ConnectionError:
            return "No internet connection"

def format_weather(data: dict) -> str:
    """Format weather data into a readable string."""
    location = data["location"]
    current = data["current"]

    return f"""
            City: {location['name']}, {location['country']}
            Temperature: {current['temperature']}°C
            Weather: {current['weather_descriptions'][0]}
            Wind Speed: {current['wind_speed']} km/h
            Humidity: {current['humidity']}%
            """

class SearchInput(BaseModel):
    city: str = Field(description="name of the city you want weather of")

@tool("get_weather_forecast", args_schema=SearchInput, return_direct=True)
def get_weather_forecast(city: str) -> str:
    """Get weather forecast for a city."""
    weather = Weather(city)
    data = weather.get_weather()

    if isinstance(data, str):
        return data  # Return error message

    return format_weather(data)

def get_email_body(payload):

    """Extracts the plain text body from an email payload."""

    if 'body' in payload and 'data' in payload['body']:
        try:
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        except Exception:
            return None

    if 'parts' in payload:
        for part in payload['parts']:
            
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                try:
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                except Exception:
                    return None
    return None

def get_email_attachments_details(payload):
    attachment_info = []

    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("filename"):  # Check if it's an attachment
                filename = part["filename"]
                mime_type = part.get("mimeType", "Unknown")
                size = part["body"].get("size", 0)  # Size in bytes

                attachment_info.append({
                    "filename": filename,
                    "mime_type": mime_type,
                    "size_bytes": size
                })

    return attachment_info

class list_emails_input(BaseModel):
    number_of_emails: int = Field(description="number of emails you want to fetch")
@tool("fetch_emails_in_inbox", args_schema=list_emails_input, return_direct=True)
def fetch_new_emails_in_inbox(number_of_emails: int = 10):
    """
    Fetches the latest unread emails from the Gmail inbox.

    Retrieves up to `number_of_emails` unread emails received within the last 10 days.
    Returns a list containing message ID, sender, subject, and date in ISO format.
    """
    creds = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', 
                                                  maxResults=number_of_emails,
                                                  q='is:unread newer_than:5d'
                                                  ).execute()
        messages = results.get('messages', [])

        if not messages:
            return {"message": "No new mails"}
        
        final_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')
            date_str = headers.get('Date', None)

            if date_str:
                try:
                    parsed_date = parsedate_to_datetime(date_str)
                    date_iso = parsed_date.isoformat()
                except Exception:
                    date_iso = None
            else:
                date_iso = None

            final_list.append({
                "message_id": message['id'],
                "from": sender,
                "subject": subject,
                "date": date_iso
            })

        return final_list

    except HttpError as error:
        print(f'An error occurred: {error}')
        return f'An error occurred: {error}'


class get_email_input(BaseModel):
    message_id: str = Field(description="The unique message ID of the email to fetch.")


@tool("get_email", args_schema=get_email_input, return_direct=True)
def fetch_email(message_id: str):
    """
    Fetches a complete email by message ID.

    Returns message ID, sender, subject, body text, and attachment details.
    """
    cred = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=cred)
        mail = service.users().messages().get(userId='me', id=message_id, format='full').execute()

        headers = {header['name']: header['value'] for header in mail['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown Sender')

        body = get_email_body(mail['payload'])
        attachements_details = get_email_attachments_details(mail['payload'])

        return {
            "message_id": mail['id'],
            "from": sender,
            "subject": subject,
            "body": body,
            "attachements_details": attachements_details
        }

    except HttpError as err:
        print(f'An error occurred: {err}')
        return err


class mark_email_as_read_input(BaseModel):
    message_id: str = Field(description="The message ID of the email to mark as read.")


@tool("mark_email_as_read", args_schema=mark_email_as_read_input, return_direct=True)
def mark_email_as_read(message_id: str):
    """
    Marks an email as read by removing the 'UNREAD' label.
    """
    cred = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=cred)
        service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
    
        return "Email marked as READ."
    
    except HttpError as err:
        print(f'An error occurred: {err}')
        return err


class search_emails_input(BaseModel):
    query: str = Field(description="Gmail search query (e.g., 'from:alice@gmail.com').")


@tool("search_emails", args_schema=search_emails_input, return_direct=True)
def search_emails(query: str, max_results=10):
    """
    Searches for emails matching the given query.

    Returns up to `max_results` emails, each including message ID, sender, and subject.
    """
    cred = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=cred)
        response = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = response.get("messages", [])

        if not messages:
            print('No messages found.')
            return []
        
        final_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')

            final_list.append({
                "message_id": message['id'],
                "from": sender,
                "subject": subject
            })

        return final_list
    except Exception as e:
        print("Error:", e)
        return []


class create_draft_email_input(BaseModel):
    to_email_addr: str = Field(description="Recipient's email address.")
    subject: str = Field(description="Subject of the draft email.")
    body: str = Field(description="Body content of the draft email.")


@tool("create_draft_email", args_schema=create_draft_email_input, return_direct=True)
def create_draft_email(to_email_addr: str, subject: str, body: str):
    """
    Creates an email draft with the specified recipient, subject, and body.

    Returns the draft ID.
    """
    cred = authenticate_gmail()
        
    try:
        service = build('gmail', 'v1', credentials=cred)
        message = MIMEText(body)
        message['to'] = to_email_addr
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        draft = {'message': {'raw': raw_message}}
        draft = service.users().drafts().create(userId="me", body=draft).execute()

        return {"draft_id": draft['id']}
    
    except Exception as e:
        print("Error:", e)
        return e


@tool("list_draft_emails", return_direct=True)
def list_draft_emails():
    """
    Lists all existing email drafts.

    Returns draft ID, recipient email, and subject for each draft.
    """
    cred = authenticate_gmail()
        
    try:
        service = build('gmail', 'v1', credentials=cred)

        drafts = service.users().drafts().list(userId="me").execute()
        draft_list = []
        
        if "drafts" in drafts:
            for draft in drafts["drafts"]:
                draft_id = draft["id"]
                draft_data = service.users().drafts().get(userId="me", id=draft_id).execute()
                message = draft_data.get("message", {})
                headers = message.get("payload", {}).get("headers", [])
                
                to_email = subject = "Unknown"
                for header in headers:
                    if header["name"] == "To":
                        to_email = header["value"]
                    elif header["name"] == "Subject":
                        subject = header["value"]
                
                draft_list.append({
                    "draft_id": draft_id,
                    "to_email": to_email,
                    "subject": subject
                })
            
            return draft_list
        
        return []
            
    except Exception as e:
        print("Error:", e)
        return []


class send_draft_input(BaseModel):
    draft_id: str = Field(description="The ID of the draft email to send.")


@tool("send_draft", args_schema=send_draft_input, return_direct=True)
def send_draft(draft_id: str):
    """
    Sends a draft email by its draft ID.

    Returns a confirmation message upon success.
    """
    cred = authenticate_gmail()
        
    try:
        service = build('gmail', 'v1', credentials=cred)
        service.users().drafts().send(userId="me", body={'id': draft_id}).execute()

        return {"message": "Email sent successfully"}
    except Exception as e:
        print("Error:", e)
        return e


class send_notification_input(BaseModel):
    notification_message: str = Field(description="The notification message to be sent to the user's phone.")


@tool("send_notification", args_schema=send_notification_input, return_direct=True)
def send_notification(notification_message: str):
    """
    Sends a notification to the user's phone via ntfy.sh.

    Returns success message if the notification was sent.
    """
    try:
        requests.post("https://ntfy.sh/AI-personal-manager",
                      data=notification_message.encode('utf-8'))
        return "Notification sent successfully"
    
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}

class CreateEventInput(BaseModel):
    """
    Input schema for creating a new calendar event.
    """
    title: str = Field(description="Short, descriptive title of the event (e.g., 'Submit Internship Form').")
    description: str = Field(description="Detailed description or notes about the event.")
    start_time: datetime = Field(description="Start date and time of the event in ISO format (e.g., '2025-07-21T14:00:00').")
    end_time: datetime = Field(description="End date and time of the event in ISO format.")
    tags: List[str] = Field(description="List of tags for categorization (e.g., ['urgent', 'college', 'internship']).")
    reminder_interval: int = Field(description="Minimum interval *in seconds* between reminders for this event (e.g., 14400 for 4 hours).")
    importance_level: Literal['high', 'moderate', 'low'] = Field(description="Priority level of the event affecting notification urgency.")

@tool("create_event", args_schema=CreateEventInput, return_direct=True)
def create_event_tool(**kwargs):
    """Creates a new event in your personal event database with custom notification logic.
    """
    try:
        event = create_event(
            title=kwargs.get('title'),
            description=kwargs.get('description'),
            importance_level=kwargs.get('importance_level'),
            tags=kwargs.get('tags'),
            reminder_interval=kwargs.get('reminder_interval'),
            start_time=kwargs.get('start_time'),
            end_time=kwargs.get('end_time'),
        )

        return {"message": f"New event '{event.title}' created successfully. with event id {event.id}"}
    except Exception as e:
        print(f"❌ create_event error: {e}")
        return f"create_event: {e}"

@tool("get_upcoming_events_tool", return_direct=True)
def get_upcoming_events_tool():
    """Fetches upcoming events (those starting in the future) from your personal events database,
    ordered by start time ascending.
    """
    try:

        events = get_upcoming_events()
        
        return {"events": events}

    except Exception as e:
        print(f"❌ get_upcoming_events_tool error: {e}")
        return f"get_upcoming_events_tool: {e}"

@tool("get_ongoing_events_tool", return_direct=True)
def get_ongoing_events_tool():
    """Fetches ongoing events: events that have already started but not yet ended.
    Useful to see what is currently active or in progress.
    """
    try:

        events = get_ongoing_events()

        # If needed: serialize to list of dicts here
        # events_data = [e.to_dict() for e in events]

        return {"events": events}

    except Exception as e:
        print(f"❌ get_ongoing_events_tool error: {e}")
        return f"get_ongoing_events_tool: {e}"

class create_reminder_input(BaseModel):
    title: str = Field(description="Title of the reminder")
    notification_message: str = Field(description="Notification message for reminder.")
    reminder_time: datetime = Field(description="Time when you want to remind user. pass an ISO string of date and time.")

@tool("create_reminder", args_schema=create_reminder_input, return_direct=True)
def create_reminder_tool(title: str, notification_message: str, reminder_time: datetime):
    """Creates a reminder for user that'll send notificaton to user automatically."""
    try:
        reminder = create_reminder(
            title=title,
            notification_message=notification_message,
            reminder_time=reminder_time
        )
        return {"message": f"New reminder '{reminder.title}' created successfully with id {reminder.id}."}
    except Exception as e:
        print("create_reminder_tool: ", e)
        return f"create_reminder_tool: {e}"


@tool("get_upcoming_reminders_tool", return_direct=True)
def get_upcoming_reminders_tool():
    """
    Returns a list of upcoming reminders in user's personal database.
    """
    try:
        reminders = get_upcoming_reminders()

        return {"remindes": reminders}
    except Exception as e:
        print("get_upcoming_reminders_tool: ",e)
        return f"get_upcoming_reminders_tool: {e}"




event_schedular_tools = [create_event_tool, get_upcoming_events, get_ongoing_events_tool]

tools = [
    get_weather_forecast, 
    fetch_new_emails_in_inbox, 
    fetch_email, 
    mark_email_as_read, 
    search_emails,
    create_draft_email,
    list_draft_emails,
    send_draft,
    send_notification,
    create_event_tool,
    get_upcoming_events_tool,
    get_ongoing_events_tool,
    create_reminder_tool,
    get_upcoming_reminders_tool
]

