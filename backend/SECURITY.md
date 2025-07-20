# 🔒 Security Guide

## ⚠️ CRITICAL: Protect Your Credentials

### **Files That Should NEVER Be Committed to Git:**

1. **`.env.local`** - Your real API keys and database credentials
2. **`credentials.json`** - Gmail OAuth credentials  
3. **`token.json`** - Gmail access tokens
4. **Any `.key`, `.pem` files** - Private keys

### **Safe Files to Commit:**
- **`.env`** - Template with placeholder values
- **`.env.example`** - Example configuration

## 🛡️ Setup Your Credentials Safely

### Step 1: Create Local Environment File
```bash
# Copy the template
cp .env .env.local

# Edit with your real credentials
nano .env.local
```

### Step 2: Add Your Real Credentials to `.env.local`
```env
# Real database URL
DATABASE_URL=postgresql://your_real_credentials_here

# Real API keys
GOOGLE_API_KEY=your_actual_google_api_key
MEM0_API_KEY=your_actual_mem0_api_key
OPENROUTER_API_KEY=your_actual_openrouter_key
```

### Step 3: Verify Git Ignores Sensitive Files
```bash
# Check what Git will track
git status

# These should NOT appear:
# - .env.local
# - credentials.json  
# - token.json
```

## 🔍 Check for Accidentally Committed Secrets

### Before Pushing to GitHub:
```bash
# Scan for potential secrets
git log --oneline | head -10
git show HEAD  # Review your latest commit

# If you accidentally committed secrets:
git reset --soft HEAD~1  # Undo last commit (keeps changes)
# Remove sensitive files, then commit again
```

### Emergency: Secrets Already Pushed
1. **Immediately rotate all API keys**
2. **Change database passwords**
3. **Revoke and regenerate OAuth credentials**
4. **Consider repository as compromised**

## 🚀 Production Deployment Security

### Environment Variables in Render/Cloud:
```env
# Set these in your hosting platform's environment variables
DATABASE_URL=your_production_db_url
GOOGLE_API_KEY=your_production_api_key
MEM0_API_KEY=your_production_mem0_key
OPENROUTER_API_KEY=your_production_openrouter_key
```

### Docker Security:
```bash
# Use environment variables, not files
docker run -e DATABASE_URL=your_db_url -e GOOGLE_API_KEY=your_key your-image

# Or use Docker secrets for production
docker secret create db_url your_database_url.txt
```

## 🔧 Security Best Practices

### 1. **API Key Rotation**
- Rotate keys every 90 days
- Use different keys for development/production
- Monitor API usage for anomalies

### 2. **Database Security**
- Use strong, unique passwords
- Enable SSL/TLS connections
- Restrict network access
- Regular backups

### 3. **OAuth Security**
- Keep `credentials.json` secure
- Regenerate if compromised
- Use minimal required scopes
- Monitor authorized applications

### 4. **Application Security**
```python
# Configure CORS properly for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🚨 Security Checklist

### Before Going Live:
- [ ] All sensitive files in `.gitignore`
- [ ] API keys in environment variables only
- [ ] Database uses strong credentials
- [ ] CORS configured for production
- [ ] SSL/HTTPS enabled
- [ ] Regular security updates planned
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented

### Regular Maintenance:
- [ ] Monthly API key rotation
- [ ] Quarterly dependency updates
- [ ] Monitor access logs
- [ ] Review API usage patterns
- [ ] Check for security advisories

## 🆘 If Security Is Compromised

### Immediate Actions:
1. **Stop the application**
2. **Rotate all credentials immediately**
3. **Review access logs**
4. **Assess data exposure**
5. **Notify users if necessary**
6. **Update security measures**
7. **Restart with new credentials**

### Investigation:
- Check Git history for leaked secrets
- Review application logs
- Monitor API usage for unusual patterns
- Verify database integrity

---

**Remember: Security is not a one-time setup, it's an ongoing process!** 🔒
