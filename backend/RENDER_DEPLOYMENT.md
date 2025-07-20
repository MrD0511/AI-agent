# 🚀 Deploy to Render - Complete Guide

## Method 1: One-Click Deploy with render.yaml

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Method 2: Manual Deployment

### Step 1: Prepare Your Repository

1. **Push your code** to GitHub (make sure it's the latest version)
2. **Ensure sensitive files are NOT in git**:
   - `.env.local` should be git-ignored ✅
   - `credentials.json` should be git-ignored ✅

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### Step 3: Create PostgreSQL Database

1. **New** → **PostgreSQL**
2. **Name**: `ai-personal-manager-db`
3. **Database**: `ai_personal_manager`  
4. **User**: `ai_user`
5. **Plan**: Free (or paid for production)
6. **Create Database**
7. **Copy the Internal Database URL** (starts with `postgresql://...`)

### Step 4: Create Web Service

1. **New** → **Web Service**
2. **Connect Repository**: Select your AI-agent repo
3. **Runtime**: Python 3
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. **Plan**: Free (or paid for production)

### Step 5: Configure Environment Variables

In the **Environment** tab, add:

```
ENVIRONMENT=production
PYTHONPATH=/opt/render/project/src

# Database (use the Internal URL from Step 3)
DATABASE_URL=postgresql://ai_user:password@dpg-xxxxx-a/ai_personal_manager

# API Keys (get new ones - old ones were compromised)
GOOGLE_API_KEY=your_new_google_api_key
MEM0_API_KEY=your_new_mem0_api_key  
OPENROUTER_API_KEY=your_new_openrouter_api_key

# Optional
WEATHERSTACK_API_KEY=your_weatherstack_key
NTFY_TOPIC=AI-personal-manager
```

### Step 6: Deploy

1. **Create Web Service**
2. Wait for deployment (5-10 minutes)
3. Check the **Logs** for any errors
4. Visit your app URL (will be like `https://ai-personal-manager-xxx.onrender.com`)

### Step 7: Upload Gmail Credentials

**Option A: Via Environment (Recommended)**
- Convert your `credentials.json` to base64:
  ```bash
  base64 -i credentials.json
  ```
- Add as environment variable:
  ```
  GOOGLE_CREDENTIALS_B64=ewogICJpbnN0YWxsZWQiOiB7...
  ```

**Option B: Manual Upload**
- Use Render's file upload feature
- Upload `credentials.json` to `/opt/render/project/src/`

### Step 8: Test Your Deployment

Visit these endpoints:
- `https://your-app.onrender.com/` - API info
- `https://your-app.onrender.com/health` - Health check
- `https://your-app.onrender.com/docs` - API documentation

## 🔧 Production Optimizations

### Scaling
- **Free Tier**: Sleeps after 15 min of inactivity
- **Paid Tier**: Always-on, faster performance
- **Background Jobs**: Will pause on free tier when sleeping

### Performance
```yaml
# In render.yaml - add these for better performance
envVars:
  - key: WEB_CONCURRENCY
    value: 4
  - key: MAX_WORKERS
    value: 1
```

### Monitoring
- Enable **Health Checks** (already configured)
- Set up **Alerts** in Render dashboard
- Monitor **Logs** for background job execution

## 🔐 Security for Production

### 1. Update CORS for Production
```python
# In app.py - restrict CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 2. Environment-Specific Settings
```python
# Add to app.py
import os
DEBUG = os.environ.get("ENVIRONMENT") != "production"
```

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check `requirements.txt` formatting
   - Ensure Python version compatibility

2. **App Won't Start**
   - Check logs for missing environment variables
   - Verify PORT configuration

3. **Database Connection Failed**
   - Verify DATABASE_URL format
   - Check if database is created and running

4. **Background Jobs Not Running**
   - Free tier: Jobs pause when app sleeps
   - Upgrade to paid tier for 24/7 operation

5. **Gmail Authentication Fails**
   - Verify `credentials.json` is uploaded
   - Check Google Cloud Console settings
   - Ensure OAuth scopes are correct

### Logs to Check:
```bash
# Email processing
🔄 Running background email agent...
✅ Background email processing completed

# Scheduler
🚀 Starting AI Personal Manager...
✅ All background processes started successfully

# Health checks
{"status": "healthy", "scheduler_running": true}
```

## 🎉 Success!

Your AI Personal Manager is now:
- ✅ **Running 24/7** on Render
- ✅ **Automatically processing emails** every 4 hours
- ✅ **Sending notifications** via ntfy.sh
- ✅ **Monitoring deadlines** and events
- ✅ **Secure** with environment variables
- ✅ **Scalable** with PostgreSQL database

**Access your API**: `https://your-app.onrender.com`
**API Docs**: `https://your-app.onrender.com/docs`

---

🎯 **Next Steps**: Build a frontend that connects to your API!
