# AI Personal Manager Deployment Guide

## 🚀 Quick Deploy to Render

### Step 1: Fork this repository

### Step 2: Create accounts and get API keys
- **Google AI Studio**: Get your Gemini API key
- **Mem0**: Sign up and get your API key  
- **OpenRouter** (optional): For alternative LLM models

### Step 3: Set up Gmail API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop application)
5. Download `credentials.json`

### Step 4: Deploy to Render

#### Option A: Docker Deployment (Recommended)
1. Connect your GitHub repo to Render
2. Create a new **Web Service**
3. Use Docker environment
4. Set environment variables:
   ```
   GOOGLE_API_KEY=your_gemini_api_key
   MEM0_API_KEY=your_mem0_api_key
   OPENROUTER_API_KEY=your_openrouter_key
   DATABASE_URL=your_postgres_url
   ```

#### Option B: Native Python Deployment
1. Runtime: Python 3.13
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Step 5: Database Setup
- Add PostgreSQL add-on in Render
- Copy the connection string to `DATABASE_URL`

### Step 6: Upload Gmail Credentials
- Upload your `credentials.json` to the deployment
- First time: Visit `/auth` endpoint to authenticate

### Step 7: Customize Settings (Optional)
- Modify background job intervals in `app.py`
- Adjust notification preferences
- Configure your timezone

## 🛠️ Local Development

```bash
# Clone repository
git clone <your-repo>
cd ai-personal-manager

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
python -c "from src.db import engine; from src.db.models import Base; Base.metadata.create_all(bind=engine)"

# Start the application
uvicorn app:app --reload
```

## 🐳 Docker Deployment

```bash
# Using Docker Compose (includes PostgreSQL)
docker-compose up -d

# Or build and run manually
docker build -t ai-personal-manager .
docker run -p 8000:8000 ai-personal-manager
```

## 📱 Frontend Integration

The API provides comprehensive endpoints for building a frontend:

- `GET /` - API info and status
- `POST /chat` - Chat with AI assistant
- `GET /reminders` - Get upcoming reminders
- `GET /events/upcoming` - Get upcoming events
- `POST /trigger/email-check` - Manual email processing
- `POST /notification/send` - Send manual notifications

## 🔧 Configuration

### Background Process Intervals
Edit in `app.py`:
```python
# Email processing: Every 4 hours
hours=4

# Reminder checks: Every 5 minutes  
minutes=5

# Deadline monitoring: Every 30 minutes
minutes=30
```

### Notification Settings
- Default: Uses ntfy.sh (no setup required)
- Custom: Modify `send_notification` in `tools.py`

## 🔒 Security Best Practices

1. **API Keys**: Never commit to version control
2. **Gmail Credentials**: Store securely, rotate regularly
3. **Database**: Use strong passwords
4. **CORS**: Configure properly for production
5. **Rate Limiting**: Consider adding for public deployments

## 🆘 Troubleshooting

### Common Issues:
1. **Gmail API Quota**: Check quotas in Google Cloud Console
2. **Database Connection**: Verify DATABASE_URL format
3. **Background Jobs**: Check logs for scheduler errors
4. **Memory Usage**: Monitor for large email processing

### Logs:
- Check application logs in Render dashboard
- Use `/health` endpoint for status monitoring
- Background job status available at `/status`

## 🎯 Usage Examples

### Email Management:
- "Check my latest emails"
- "Summarize important emails from today"
- "Mark all emails as read"

### Scheduling:
- "Schedule meeting tomorrow at 3 PM"
- "Remind me about project deadline next week" 
- "What's on my calendar today?"

### Notifications:
- "Send me a reminder in 2 hours"
- "Notify me 30 minutes before my meeting"

## 🔄 Updates and Maintenance

1. **Pull latest changes** from main branch
2. **Redeploy** on Render (automatic with GitHub integration)
3. **Monitor logs** for any issues
4. **Update API keys** as needed

---

**🎉 You're all set! Your personal AI assistant is now running 24/7 in the cloud.**
