from langchain_core.messages import HumanMessage
from src.pretty_printing import pretty_print_messages
from src.agents import create_agentic_workflow, create_background_email_agent
from src.db import engine
from src.services.prompts import background_emai_agent_command
from src.db.models import Base
from src.db.crud.reminders import get_upcoming_reminders
from src.db.crud.events import get_upcoming_events, get_ongoing_events
from src.tools.tools import send_notification
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import uvicorn

# Load environment variables securely
load_dotenv('.env.local')  # Load local credentials first (never committed)
load_dotenv()  # Fall back to template .env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) 

app = FastAPI(
    title="AI Personal Manager",
    description="Self-hosted AI assistant for email management, scheduling, and notifications",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
scheduler = BackgroundScheduler()
bk_chat_history = []
background_email_agent = create_background_email_agent(bk_chat_history)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("✅ Database tables created successfully!")
    except Exception as e:
        logging.error(f"❌ Database initialization failed: {e}")
        raise

# def run_chat():
#     chat_history = []

#     agent = create_agentic_workflow(chat_history)
#     config = {"configurable": {"thread_id": "1"}}

#     # try:
#     #     with open('graph_new.png', 'wb') as f:
#     #         f.write(agent.get_graph().draw_mermaid_png())
#     #     print("Image saved as graph.png")
#     # except Exception as e:
#     #     # This requires some extra dependencies and is optional
#     #     print("execprtion display", e.with_traceback(None))
#     #     pass

#     # 🗣 CLI loop

#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             break
#         chat_history.append(HumanMessage(content=user_input))

#         for chunk in agent.stream({"messages": chat_history}, config):
#             pretty_print_messages(chunk)

def background_email_agent_process():
    """Process emails every 4 hours"""
    logging.info("🔄 Running background email agent...")
    config = {"configurable": {"thread_id": "email_bg"}}
    try:
        with open('graph_new.png', 'wb') as f:
            f.write(background_email_agent.get_graph().draw_mermaid_png())
        print("📊 Workflow graph saved as graph_new.png")
    except Exception as e:
        logging.warning(f"Graph generation failed: {e}")
        
    bk_chat_history.append(HumanMessage(background_emai_agent_command))
    
    for chunk in background_email_agent.stream({"messages": bk_chat_history}, config):
        pretty_print_messages(chunk)
    
    logging.info("✅ Background email processing completed")

def check_reminders():
    """Check and send due reminders"""
    logging.info("🔔 Checking reminders...")
    try:
        reminders = get_upcoming_reminders()
        current_time = datetime.now()
        
        for reminder in reminders:
            reminder_time = datetime.fromisoformat(reminder['reminder_time'].replace('Z', '+00:00'))
            # Check if reminder is due (within next 5 minutes)
            if reminder_time <= current_time + timedelta(minutes=5) and not reminder['is_notification_sent']:
                send_notification(f"⏰ Reminder: {reminder['title']} - {reminder['notification_message']}")
                logging.info(f"📤 Sent reminder: {reminder['title']}")
                
    except Exception as e:
        logging.error(f"❌ Reminder check failed: {e}")

def check_event_deadlines():
    """Check for upcoming event deadlines and notify"""
    logging.info("📅 Checking event deadlines...")
    try:
        upcoming_events = get_upcoming_events()
        current_time = datetime.now()
        
        for event in upcoming_events:
            if event['start_time']:
                event_time = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                time_until_event = event_time - current_time
                
                # Notify for high importance events 1 day before
                if event['importance_level'] == 'high' and timedelta(hours=23) <= time_until_event <= timedelta(hours=25):
                    send_notification(f"🚨 Important Event Tomorrow: {event['title']} at {event['start_time']}")
                    logging.info(f"📤 Sent high priority reminder: {event['title']}")
                
                # Notify for all events 2 hours before
                elif timedelta(hours=1.5) <= time_until_event <= timedelta(hours=2.5):
                    send_notification(f"⏳ Upcoming Event: {event['title']} in 2 hours")
                    logging.info(f"📤 Sent 2-hour reminder: {event['title']}")
                    
    except Exception as e:
        logging.error(f"❌ Event deadline check failed: {e}")

@app.on_event("startup")
def start_scheduler():
    init_db()
    logging.info("🚀 Starting AI Personal Manager...")
    
    # Email processing every 4 hours
    scheduler.add_job(
        background_email_agent_process, 
        'interval', 
        hours=4,
        id='email_processor',
        name='Background Email Processing'
    )
    
    # Check reminders every 5 minutes
    scheduler.add_job(
        check_reminders,
        'interval',
        minutes=5,
        id='reminder_checker',
        name='Reminder Notifications'
    )
    
    # Check event deadlines every 30 minutes
    scheduler.add_job(
        check_event_deadlines,
        'interval',
        minutes=30,
        id='deadline_checker', 
        name='Event Deadline Monitoring'
    )
    
    scheduler.start()
    logging.info("✅ All background processes started successfully")
    logging.info("📧 Email processing: Every 4 hours")
    logging.info("🔔 Reminder checks: Every 5 minutes") 
    logging.info("📅 Deadline monitoring: Every 30 minutes")

@app.on_event("shutdown")
def shutdown_scheduler():
    logging.info("Shutting down scheduler...")
    scheduler.shutdown()
    logging.info("Scheduler stopped.")

@app.get('/')
async def root():
    return {
        "message": "🤖 AI Personal Manager API",
        "version": "1.0.0",
        "description": "Self-hosted AI assistant for email, scheduling & notifications",
        "status": "running",
        "background_processes": {
            "email_processing": "Every 4 hours",
            "reminder_checks": "Every 5 minutes", 
            "deadline_monitoring": "Every 30 minutes"
        }
    }

@app.get('/health')
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler.running,
        "active_jobs": len(scheduler.get_jobs()),
        "timestamp": datetime.now().isoformat()
    }

@app.get('/status')
async def get_detailed_status():
    """Detailed status of all background processes"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {
        "scheduler_running": scheduler.running,
        "jobs": jobs,
        "system_time": datetime.now().isoformat()
    }

@app.post('/trigger/email-check')
async def trigger_email_check():
    """Manually trigger email processing"""
    try:
        background_email_agent_process()
        return {"message": "✅ Email processing triggered successfully", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email processing failed: {str(e)}")

@app.post('/trigger/reminder-check')
async def trigger_reminder_check():
    """Manually trigger reminder check"""
    try:
        check_reminders()
        return {"message": "✅ Reminder check triggered successfully", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reminder check failed: {str(e)}")

@app.post('/trigger/deadline-check')
async def trigger_deadline_check():
    """Manually trigger deadline monitoring"""
    try:
        check_event_deadlines()
        return {"message": "✅ Deadline check triggered successfully", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deadline check failed: {str(e)}")

@app.get('/reminders')
async def get_reminders():
    """Get all upcoming reminders"""
    try:
        reminders = get_upcoming_reminders()
        return {"reminders": reminders, "count": len(reminders)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reminders: {str(e)}")

@app.get('/events/upcoming')
async def get_upcoming_events_api():
    """Get all upcoming events"""
    try:
        events = get_upcoming_events()
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

@app.get('/events/ongoing')
async def get_ongoing_events_api():
    """Get all ongoing events"""
    try:
        events = get_ongoing_events()
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ongoing events: {str(e)}")

@app.post('/notification/send')
async def send_manual_notification(message: str):
    """Send a manual notification"""
    try:
        result = send_notification(message)
        return {"message": "✅ Notification sent successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

# Chat endpoint for frontend interaction
@app.post('/chat')
async def chat_with_assistant(message: str):
    """Chat with the AI assistant"""
    try:
        chat_history = []
        agent = create_agentic_workflow(chat_history)
        config = {"configurable": {"thread_id": f"chat_{datetime.now().timestamp()}"}}
        
        chat_history.append(HumanMessage(content=message))
        
        responses = []
        for chunk in agent.stream({"messages": chat_history}, config):
            # Collect response chunks
            for node_name, node_update in chunk.items():
                if 'messages' in node_update and node_update['messages']:
                    last_message = node_update['messages'][-1]
                    if hasattr(last_message, 'content') and last_message.content:
                        responses.append({
                            "node": node_name,
                            "content": last_message.content,
                            "type": type(last_message).__name__
                        })
        
        return {
            "message": message,
            "responses": responses,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app=app, host="0.0.0.0", port=port)