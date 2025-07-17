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
def fetch_emails_in_inbox(number_of_emails : int = 10) :

    """Lists emails in Inbox"""

    creds = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=number_of_emails).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return
        
        final_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')

            final_list.append({
                "message_id": message['id'],
                "from": sender,
                "subject" : subject
            })

        return final_list

    except HttpError as error:
        print(f'An error occurred: {error}')
            
class get_email_input(BaseModel):
    message_id: str = Field(description="message_id of email you want to fetch")

@tool("get_email", args_schema=get_email_input, return_direct=True)
def fetch_email(message_id: str):
    
    """read Email by message_id"""

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
            "subject" : subject,
            "body": body,
            "attachements_details": attachements_details
        }

    except HttpError as err:
        print(f'An error occurred: {err}')
        return err

class mark_email_as_read_input(BaseModel):
    message_id: str = Field("message id of the email you want to mark as read")

@tool("mark_email_as_read", args_schema=mark_email_as_read_input, return_direct=True)
def mark_email_as_read(message_id: str):
    """Marks email as read by removing UNREAD lable"""

    cred = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=cred)
        mail = service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
    
        return "Email marked as UNREAD."
    
    except HttpError as err:
        print(f'An error occurred: {err}')
        return err

class search_emails_input(BaseModel):
    query: str = Field(description="Query to search emails")

@tool("search_emails", args_schema=search_emails_input, return_direct=True)
def search_emails(query: str, max_results=10):
    """
    Searches for emails matching the given query.

    :param service: Authorized Gmail API service instance
    :param query: Gmail search query (e.g., "from:example@gmail.com subject:Meeting")
    :param max_results: Maximum number of emails to retrieve
    :return: List of matching email message IDs
    """
    cred = authenticate_gmail()

    try:
        service = build('gmail', 'v1', credentials=cred)
        response = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = response.get("messages", [])

        if not messages:
            print('No messages found.')
            return
        
        final_list = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')

            final_list.append({
                "message_id": message['id'],
                "from": sender,
                "subject" : subject
            })

        return final_list
    except Exception as e:
        print("Error:", e)
        return []

class create_draft_email_input(BaseModel):
    to_email_addr: str = Field(description="Recipients email address")
    subject: str = Field(description="Subject of the email draft")
    body: str = Field(description="Body of the draft email")

@tool("create_draft_email", args_schema=create_draft_email_input, return_direct=True)
def create_draft_email(to_email_addr: str, subject: str , body: str ):
    """Creates a Draft of email
    param to_email: The email whom you want to send the email
    param subject: Subject of the email
    param body: The body of the email
    """
    cred = authenticate_gmail()
        
    try:
        service = build('gmail', 'v1', credentials=cred)
        message = MIMEText(body)
        message['to'] = to_email_addr
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        # Draft email
        draft = {
            'message': {
                'raw': raw_message
            }
        }

        draft = service.users().drafts().create(userId="me", body=draft).execute()

        draft_id = draft['id']
        return {
            "draft_id": draft_id
        }
    
    except Exception as e:
        print("Error:", e)
        return e


@tool("list_draft_emails", return_direct=True)
def list_draft_emails():

    """This tool fetches the email drafts
    
    -It optionally requires number of draft emails we want to fetch.
    """

    cred = authenticate_gmail()
        
    try:
        service = build('gmail', 'v1', credentials=cred)

        drafts = service.users().drafts().list(userId="me").execute()
        draft_list = []
        
        if "drafts" in drafts:
            for draft in drafts["drafts"]:
                draft_id = draft["id"]
                
                # Get full draft details
                draft_data = service.users().drafts().get(userId="me", id=draft_id).execute()
                message = draft_data.get("message", {})
                headers = message.get("payload", {}).get("headers", [])
                
                to_email = subject = "Unknown"
                
                # Extract 'To' and 'Subject' from headers
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
    draft_id: str = Field(description="Id of the draft that you want to send")

@tool("send_draft", args_schema=send_draft_input, return_direct=True)
def send_draft(draft_id : str):
    """Description of"""

    cred = authenticate_gmail()
        
    try:
        service = build('gmail', 'v1', credentials=cred)
        sent_message = service.users().drafts().send(userId="me", body={'id': draft_id}).execute()

        return {
            "message": "Email sent successfully"
        }
    except Exception as e:
        print("Error:", e)
        return e           


@tool("list_upcoming_events_of_calender", return_direct=True)
def list_upcoming_events_of_calender():
    """
    This tool fetches the next 10 upcoming events from the user's Google Calendar.
    """
    cred = authenticate_gmail()  # Make sure this includes calendar scope

    try:
        service = build("calendar", "v3", credentials=cred)
        now = datetime.utcnow().isoformat() + "Z"  # UTC time
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if not events:
            return [{"message": "No upcoming events found."}]

        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append({
                "event_id": event["id"],
                "summary": event.get("summary", "No Title"),
                "start": start,
            })

        return event_list

    except Exception as e:
        print("Error:", e)
        return [{"error": str(e)}]

class create_new_calender_event_input(BaseModel):
    summary: str = Field(description="summary of the calender event")
    start_time: str = Field(description="Start of the event")
    end_time: str = Field(description="end time of the event")
    description: str = Field(description="Description of the event")
    timezone: str = Field(description="Timezone of the event")

@tool("create_new_calender_event", args_schema=create_new_calender_event_input, return_direct=True)
def create_new_calender_event(summary: str, start_time: str, end_time: str, description: str = "", timezone: str = "UTC"):
    """
    Creates a new calendar event.

    Args:
    - summary: Title of the event.
    - start_time: Start time in ISO format (e.g. "2025-04-11T10:00:00").
    - end_time: End time in ISO format.
    - description: (Optional) Description of the event.
    - timezone: (Optional) Timezone (default is "UTC").
    """

    cred = authenticate_gmail()

    try:
        service = build("calendar", "v3", credentials=cred)

        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": timezone,
            },
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return {
            "message": "Event created successfully!",
            "event_id": created_event["id"],
            "summary": created_event["summary"],
            "start": created_event["start"]["dateTime"],
            "end": created_event["end"]["dateTime"]
        }

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}

class delete_event_input(BaseModel):
    event_id: str = Field(description="Id of the calender event")

@tool("delete_event", args_schema=delete_event_input, return_direct=True)
def delete_calender_event(event_id: str):
    """
    Deletes a calendar event by its event ID.
    """
    cred = authenticate_gmail()

    try:
        service = build("calendar", "v3", credentials=cred)
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"message": f"Event {event_id} deleted successfully."}

    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}

class send_notification_input(BaseModel):
    notification_message: str = Field(description="The notification message")

@tool("send_notification", args_schema=send_notification_input, return_direct=True)
def send_notification(notification_message: str):
    """
    This tool can be used to send notification to the user's phone.
    """
    try:
        requests.post("https://ntfy.sh/AI-personal-manager",
        data=f"{notification_message}".encode(encoding='utf-8'))

        return "Notification sent successfully"
    
    except Exception as e:
        print("Error:", e)
        return {"error": str(e)}
    

tools = [
    get_weather_forecast, 
    fetch_emails_in_inbox, 
    fetch_email, 
    mark_email_as_read, 
    search_emails,
    create_draft_email,
    list_draft_emails,
    send_draft,
    list_upcoming_events_of_calender,
    create_new_calender_event,
    delete_calender_event, 
    send_notification
]

