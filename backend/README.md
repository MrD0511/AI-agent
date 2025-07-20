# 🤖 AI Personal Manager

**Self-hosted, open-source AI assistant that manages your emails, schedules, and notifications while keeping your data completely private.**

> 🔒 **Privacy First**: Your emails never leave your infrastructure  
> 💰 **Cost Transparent**: You control and pay for your own API usage  
> 🐳 **One-Click Deploy**: Ready-to-use Docker image for instant deployment  
> 🎨 **Customizable**: Full source code to adapt to your needs

## 🌟 Why AI Personal Manager?

### **The Problem**
- Existing email assistants require access to your private emails
- SaaS solutions are expensive and raise privacy concerns  
- No control over your data or costs
- Limited customization options

### **Our Solution**
- **100% Self-hosted**: Deploy on your own infrastructure
- **Open Source**: Full transparency and customization
- **Privacy Focused**: Your emails stay on your servers
- **Cost Effective**: Pay only for your API usage
- **Easy Deployment**: One Docker command to get started

## 🚀 Features

### 📧 **Email Management**
- **Smart Email Fetching**: Automatically retrieves and processes your latest emails
- **Intelligent Categorization**: Classifies emails by importance (Important/Moderate/Low)
- **Content Summarization**: Provides concise summaries of important emails
- **Gmail Integration**: Full Gmail API integration with OAuth2 authentication

### 📅 **Event & Schedule Management**
- **Event Creation**: Schedule events with custom reminders and importance levels
- **Smart Scheduling**: Automatically extract deadlines from emails and create events
- **Upcoming Events**: Track what's coming up in your schedule
- **Ongoing Events**: Monitor currently active events

### 🔔 **Notification System**
- **Real-time Notifications**: Instant alerts via ntfy.sh to your devices
- **Smart Reminders**: Context-aware reminders based on email content
- **Custom Alerts**: Set personalized notification schedules

### 🔄 **Background Automation**
- **Email Processing**: Runs every 4 hours automatically
- **Reminder Monitoring**: Checks every 5 minutes for due reminders  
- **Deadline Tracking**: Monitors events every 30 minutes
- **Smart Notifications**: Contextual alerts based on importance

### 🌐 **Platform Ready**
- **REST API**: Complete API for frontend integration
- **Docker Ready**: One-command deployment
- **Render Compatible**: Deploy to cloud in minutes
- **Frontend Ready**: Full API documentation for UI development

## 🏗️ Architecture

The system uses a **multi-agent architecture** with LangGraph:

```
┌─────────────────┐
│   Supervisor    │ ← Coordinates all agents
│     Agent       │
└─────────────────┘
         │
    ┌────┴─────┬──────────┬─────────────┐
    │          │          │             │
┌───▼───┐ ┌───▼───┐ ┌────▼────┐ ┌─────▼─────┐
│Email  │ │Event  │ │Notification│ │Background │
│Agent  │ │Agent  │ │   Agent    │ │  Agent    │
└───────┘ └───────┘ └─────────┘ └───────────┘
```

### Agent Responsibilities

- **📧 Email Agent**: Fetches, categorizes, and summarizes emails
- **📅 Event Scheduler Agent**: Manages calendar events and deadlines
- **🔔 Notification Agent**: Sends alerts and reminders
- **🎯 Supervisor Agent**: Orchestrates workflow and delegates tasks

## 🚀 Quick Deploy (5 Minutes)

### Option 1: Deploy to Render (Recommended)

1. **Fork this repository**
2. **Get API keys**:
   - [Google AI Studio](https://aistudio.google.com/) → Gemini API key
   - [Mem0](https://mem0.ai/) → Memory API key
3. **Deploy to Render**: [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
4. **Set environment variables** in Render dashboard
5. **Upload Gmail credentials** (see [DEPLOYMENT.md](DEPLOYMENT.md))

### Option 2: Local Docker

```bash
# Clone and run
git clone <your-fork>
cd ai-personal-manager
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
```

Visit `http://localhost:8000` - Your AI assistant is ready! 🎉

## 📖 Complete Setup Guide

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📁 Project Structure

```
backend/
├── src/
│   ├── agents/                 # AI agent implementations
│   │   ├── supervisor_agent.py    # Main coordinator
│   │   ├── email_agent.py         # Email processing
│   │   ├── event_schedular_agent.py # Calendar management
│   │   ├── notification_agent.py   # Alert system
│   │   └── background_email_agent.py # Background processing
│   ├── db/                     # Database layer
│   │   ├── models/                # SQLAlchemy models
│   │   ├── crud/                  # Database operations
│   │   └── connection.py          # DB connection
│   ├── services/               # Core services
│   │   ├── llm_models.py          # LLM configurations
│   │   ├── prompts.py             # Agent prompts
│   │   ├── agentic_supportive_tool.py # Agent utilities
│   │   └── support_services.py    # Helper functions
│   └── tools/                  # External integrations
│       └── tools.py               # Gmail, weather, notifications
├── app.py                      # Main application entry point
├── pyproject.toml             # Project dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `GOOGLE_API_KEY` | Google Gemini API key | ✅ |
| `MEM0_API_KEY` | Mem0 memory service API key | ✅ |
| `OPENROUTER_API_KEY` | OpenRouter API key | ✅ |

### Gmail API Setup

1. **Enable Gmail API** in Google Cloud Console
2. **Create OAuth2 credentials**
3. **Download credentials.json**
4. **Place in `src/` directory**
5. **First run will prompt for authentication**

### Database Schema

The system uses PostgreSQL with two main tables:

- **Events**: Stores scheduled events and deadlines
- **Reminders**: Manages notification reminders

## 🛠️ Available Commands

### Email Commands
```
"Check my emails"
"Fetch latest 5 emails"
"Summarize important emails"
"Mark email as read"
```

### Event Commands
```
"Schedule a meeting tomorrow at 3 PM"
"What's on my calendar today?"
"Remind me about the deadline"
"Show upcoming events"
```

### Notification Commands
```
"Send me a reminder in 2 hours"
"Notify me about important deadlines"
"Set daily standup reminder"
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API status and information |
| `/health` | GET | Health check for monitoring |
| `/status` | GET | Detailed background process status |
| `/chat` | POST | Interactive AI assistant chat |
| `/reminders` | GET | Get all upcoming reminders |
| `/events/upcoming` | GET | Get upcoming events |
| `/events/ongoing` | GET | Get currently active events |
| `/trigger/email-check` | POST | Manually trigger email processing |
| `/trigger/reminder-check` | POST | Manual reminder check |
| `/trigger/deadline-check` | POST | Manual deadline monitoring |
| `/notification/send` | POST | Send custom notification |

## 🎨 Frontend Development

The API is designed for easy frontend integration:

```javascript
// Example: Chat with AI assistant
const response = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: "Check my emails" })
});

// Example: Get upcoming events  
const events = await fetch('/events/upcoming').then(r => r.json());
```

## 🔄 Background Processes

The system runs three automated background processes:

1. **📧 Email Processing** (Every 4 hours)
   - Fetches new emails
   - Categorizes by importance  
   - Generates summaries
   - Creates events from deadlines
   - Sends notifications

2. **🔔 Reminder Monitoring** (Every 5 minutes)
   - Checks for due reminders
   - Sends notifications via ntfy.sh
   - Updates reminder status

3. **📅 Deadline Tracking** (Every 30 minutes)
   - Monitors upcoming events
   - Sends early warnings for important events
   - Provides timely reminders

## 🌍 Platform Vision

### **Why Open Source?**
- **Trust**: Full code transparency
- **Privacy**: Your data stays with you  
- **Customization**: Modify to your needs
- **Community**: Collaborative improvements
- **Cost Control**: No vendor lock-in

### **Who Is This For?**
- **Privacy-conscious individuals** who want email AI without data sharing
- **Developers** who want to customize their AI assistant
- **Small teams** needing shared email intelligence
- **Anyone** wanting to self-host their productivity tools

### **Deployment Options**
- **🏠 Self-hosted**: Full control on your servers
- **☁️ Cloud**: Deploy to Render, Railway, or any cloud provider  
- **🐳 Container**: Docker deployment anywhere
- **🖥️ Local**: Run on your laptop or home server

## 🚨 Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Secure your `credentials.json`** file
4. **Regularly rotate API keys**
5. **Use HTTPS** in production

## 🧪 Testing

```bash
# Run basic tests
python -m pytest tests/

# Test specific agent
python -m pytest tests/test_email_agent.py
```

## 📊 Monitoring

The system includes built-in logging and error handling:

- **Agent performance** tracking
- **API call** monitoring
- **Error logging** with context
- **Memory usage** optimization

## 🔄 Workflow Examples

### Daily Email Processing
```
1. User: "Check my emails"
2. Supervisor → Email Agent
3. Email Agent fetches → Categorizes → Summarizes
4. Notification Agent sends important alerts
5. Event Agent schedules any deadlines found
```

### Event Scheduling
```
1. User: "Remind me about the interview tomorrow"
2. Supervisor → Event Scheduler Agent
3. Creates event with reminder
4. Notification system alerts at appropriate time
```

## 🚀 Future Enhancements

- [ ] **Calendar Integration** (Google Calendar, Outlook)
- [ ] **Slack/Teams** integration
- [ ] **Voice Commands** support
- [ ] **Mobile App** companion
- [ ] **Advanced Analytics** dashboard
- [ ] **Multi-user** support
- [ ] **Plugin System** for custom tools

## 📖 API Documentation

### Core Tools

#### Email Tools
- `fetch_emails_in_inbox(number_of_emails)`: Fetch latest emails
- `get_email(message_id)`: Get complete email content
- `mark_email_as_read(message_id)`: Mark email as read
- `search_emails(query)`: Search emails by query

#### Event Tools
- `create_event(title, description, start_time, end_time, ...)`: Create new event
- `get_upcoming_events_tool()`: Get upcoming events
- `get_ongoing_events_tool()`: Get current events

#### Notification Tools
- `send_notification(message)`: Send notification to devices
- `create_reminder(title, message, time)`: Create timed reminder

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. **Check the logs** in the console output
2. **Verify API keys** and credentials
3. **Ensure database** is running
4. **Check Gmail API** quotas
5. **Open an issue** with detailed error information

## 👨‍💻 Author

**Dhruv** - AI Engineer & Developer

---

## 🙏 Acknowledgments

- **LangGraph** for the multi-agent framework
- **Google Gemini** for powerful language understanding
- **Mem0** for intelligent memory management
- **ntfy.sh** for reliable notifications

---

*Built with ❤️ for better productivity and organization*
