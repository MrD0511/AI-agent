# 🤖 AI Personal Manager

A comprehensive self-hosted AI assistant that manages your emails, schedules events, sends notifications, and helps with daily productivity tasks. Built with a multi-agent architecture using LangGraph, FastAPI, and React.

## ✨ Features

### 📧 Email Management
- **Smart Email Processing**: Automatically fetches and categorizes unread emails
- **Email Summarization**: AI-powered summaries of important emails
- **Draft Management**: Create, edit, and send email drafts
- **Search & Filter**: Advanced email search with Gmail API integration
- **Background Processing**: Automatic email checking every 4 hours

### 📅 Event & Scheduling
- **Smart Event Creation**: Natural language event scheduling
- **Deadline Monitoring**: Automatic reminders for upcoming events
- **Importance Levels**: Prioritize events with high/moderate/low importance
- **Flexible Reminders**: Custom reminder intervals for different events
- **Ongoing Event Tracking**: Monitor currently active events

### 🔔 Notification System
- **Multi-Channel Notifications**: Phone notifications via ntfy.sh
- **Smart Reminders**: Context-aware reminder notifications
- **Manual Notifications**: Send custom notifications on demand
- **Deadline Alerts**: Automatic alerts for upcoming deadlines

### 🌤️ Weather Integration
- **Real-time Weather**: Get current weather for any city
- **Location-based**: Automatic weather updates for your location

### 💾 Data Management
- **PostgreSQL Database**: Robust data storage with connection pooling
- **Memory Integration**: Long-term memory with Mem0 for context retention
- **Chat History**: Persistent conversation history
- **Data Privacy**: Self-hosted solution for complete data control

## 🏗️ Architecture

### Multi-Agent System
- **Supervisor Agent**: Orchestrates and coordinates other agents
- **Email Agent**: Handles all email-related operations
- **Event Scheduler Agent**: Manages calendar and event operations
- **Notification Agent**: Handles all notification delivery
- **Background Email Agent**: Processes emails automatically

### Technology Stack

#### Backend
- **FastAPI**: High-performance Python web framework
- **LangGraph**: Multi-agent workflow orchestration
- **SQLAlchemy**: Database ORM with connection pooling
- **PostgreSQL**: Primary database (Neon.tech cloud)
- **APScheduler**: Background task scheduling
- **Gmail API**: Email integration
- **OpenRouter**: LLM provider for AI responses

#### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and dev server
- **Real-time Streaming**: Server-sent events for live responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL database
- Gmail API credentials
- OpenRouter API key
- Mem0 API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MrD0511/AI-agent.git
   cd AI-agent/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create `.env.local` in the backend directory:
   ```env
   # Database Configuration
   database_url=your_postgresql_connection_string
   
   # API Keys
   google_api_key=your_google_api_key
   mem0_api_key=your_mem0_api_key
   openrouter_api_key=your_openrouter_api_key
   
   # Environment
   environment=development
   ```

4. **Gmail API Setup**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create credentials (OAuth 2.0 client ID)
   - Download credentials and save as `credentials.json` in `backend/app/`

5. **Database Setup**
   ```bash
   # Database tables will be created automatically on first run
   python -m app.app
   ```

6. **Start the backend server**
   ```bash
   uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   Create `.env.local` in the frontend directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

5. **Access the application**
   Open [http://localhost:5173](http://localhost:5173) in your browser

## 📖 Usage Guide

### Chat Interface
- **Natural Language**: Ask questions in plain English
- **Multi-Agent Responses**: See responses from different specialized agents
- **Tool Execution**: Expandable sections for technical operations
- **Real-time Streaming**: Watch responses as they're generated

### Example Commands
```
"Check my emails and summarize any important ones"
"Create a reminder for my meeting tomorrow at 2 PM"
"What events do I have coming up this week?"
"Send me a notification when it's time for lunch"
"What's the weather like in New York?"
"Create an event for my job interview next Friday"
```

### Dashboard Features
- **System Status**: Monitor backend processes and health
- **Recent Activity**: View latest emails, events, and reminders
- **Quick Actions**: Fast access to common operations
- **Statistics**: Overview of your productivity metrics

### Notification Management
- **Manual Notifications**: Send custom notifications to your phone
- **Automatic Reminders**: System-generated alerts for events
- **Notification History**: Track all sent notifications

## 🔧 Configuration

### API Keys & Services

#### OpenRouter (LLM Provider)
1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Add to `.env.local` as `openrouter_api_key`

#### Mem0 (Memory Service)
1. Sign up at [Mem0](https://mem0.ai/)
2. Get your API key
3. Add to `.env.local` as `mem0_api_key`

#### Neon (PostgreSQL Database)
1. Sign up at [Neon.tech](https://neon.tech/)
2. Create a new database
3. Copy connection string to `.env.local` as `database_url`

#### Ntfy.sh (Notifications)
- No signup required
- Uses public ntfy.sh service
- Topic: `AI-personal-manager`
- Download ntfy app on your phone and subscribe to the topic

### Background Processes
- **Email Processing**: Every 4 hours
- **Reminder Checks**: Every 5 minutes
- **Deadline Monitoring**: Every 30 minutes

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI Schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

### Key Endpoints
- `POST /chat` - Main chat interface with streaming responses
- `GET /reminders` - Get all upcoming reminders
- `GET /events/upcoming` - Get upcoming events
- `GET /events/ongoing` - Get currently active events
- `POST /notification/send` - Send manual notification
- `GET /health` - System health check
- `GET /status` - Detailed system status

## 🔒 Security & Privacy

### Data Privacy
- **Self-hosted**: All data stays on your infrastructure
- **No telemetry**: No data sent to external services except configured APIs
- **Encrypted connections**: HTTPS/TLS for all external communications

### Security Best Practices
- **Environment variables**: Sensitive data in `.env.local` files
- **API key rotation**: Regularly rotate your API keys
- **Database security**: Use strong database passwords
- **CORS configuration**: Configure allowed origins for production

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend && uvicorn app.app:app --reload

# Frontend
cd frontend && npm run dev
```

### Production Deployment
- **Backend**: Deploy to any Python-compatible platform (Render, Railway, etc.)
- **Frontend**: Build and deploy to any static hosting (Vercel, Netlify, etc.)
- **Database**: Use managed PostgreSQL (Neon, Supabase, AWS RDS)

### Docker Deployment
```bash
# Backend
cd backend
docker build -t ai-personal-manager-backend .
docker run -p 8000:8000 ai-personal-manager-backend

# Frontend
cd frontend
docker build -t ai-personal-manager-frontend .
docker run -p 3000:3000 ai-personal-manager-frontend
```

## 🛠️ Development

### Project Structure
```
AI-agent/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # LangGraph agents
│   │   ├── db/             # Database models & CRUD
│   │   ├── services/       # Shared services
│   │   ├── tools/          # Agent tools
│   │   └── app.py          # Main FastAPI app
│   ├── requirements.txt    # Python dependencies
│   └── .env.local         # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── api/           # API integration
│   │   ├── types/         # TypeScript types
│   │   └── App.tsx        # Main app component
│   ├── package.json       # Node dependencies
│   └── .env.local        # Frontend environment
└── README.md             # This file
```

### Adding New Features
1. **New Agent**: Create in `backend/app/agents/`
2. **New Tool**: Add to `backend/app/tools/`
3. **New API Endpoint**: Add to `backend/app/app.py`
4. **New Frontend Component**: Create in `frontend/src/components/`

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📊 Performance Optimizations

### Database
- **Connection Pooling**: Reuses database connections
- **Query Optimization**: Efficient SQLAlchemy queries
- **Indexed Columns**: Optimized database indexes

### Backend
- **Async Operations**: Non-blocking API endpoints
- **Streaming Responses**: Real-time data delivery
- **Background Tasks**: Scheduled processing
- **Caching**: Memory caching for frequently accessed data

### Frontend
- **Code Splitting**: Lazy loading of components
- **Optimized Builds**: Vite for fast builds
- **Efficient Rendering**: React best practices

## 🐛 Troubleshooting

### Common Issues

#### Gmail Authentication
```bash
# Error: credentials.json not found
# Solution: Download credentials from Google Cloud Console
```

#### Database Connection
```bash
# Error: connection refused
# Solution: Check database URL and ensure PostgreSQL is running
```

#### API Key Issues
```bash
# Error: API key invalid
# Solution: Verify all API keys in .env.local are correct
```

#### Port Conflicts
```bash
# Error: port already in use
# Solution: Change ports in configuration or kill existing processes
```

### Logs & Debugging
- **Backend logs**: Check terminal output for FastAPI server
- **Frontend logs**: Check browser console for React errors
- **Database logs**: Enable SQL logging in development
- **Agent debugging**: Enable verbose logging in LangGraph

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/MrD0511/AI-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MrD0511/AI-agent/discussions)
- **Email**: Support via GitHub only

## 🙏 Acknowledgments

- **LangGraph**: For the multi-agent framework
- **FastAPI**: For the excellent web framework
- **React**: For the frontend framework
- **OpenRouter**: For LLM API access
- **Neon**: For PostgreSQL hosting
- **Mem0**: For memory management

---

**Built with ❤️ by [MrD0511](https://github.com/MrD0511)**

*AI Personal Manager - Your intelligent assistant for productivity and organization*
