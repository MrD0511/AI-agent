# AI Personal Manager Configuration

# Background Process Intervals (in minutes)
EMAIL_PROCESSING_INTERVAL_HOURS = 4
REMINDER_CHECK_INTERVAL_MINUTES = 5  
DEADLINE_CHECK_INTERVAL_MINUTES = 30

# Email Settings
EMAIL_BATCH_SIZE = 10
EMAIL_DAYS_BACK = 10
MARK_EMAILS_AS_READ = True

# Notification Settings
NOTIFICATION_SERVICE = "ntfy"  # Options: ntfy, custom
NTFY_TOPIC = "AI-personal-manager"
HIGH_PRIORITY_ADVANCE_HOURS = 24
STANDARD_REMINDER_HOURS = 2

# AI Model Settings
PRIMARY_MODEL = "gemini-2.0-flash-001"
FAST_MODEL = "gemini-2.0-flash-lite-001"
ALTERNATIVE_MODEL = "deepseek/deepseek-chat:free"

# Memory Settings
ENABLE_MEMORY = True
MEMORY_USER_ID = "default_user"

# Timezone (for local time conversions)
TIMEZONE = "Asia/Kolkata"

# Security Settings
ALLOWED_ORIGINS = ["*"]  # Configure for production
ENABLE_CORS = True

# Logging
LOG_LEVEL = "INFO"
ENABLE_DEBUG_LOGS = False

# Feature Flags
ENABLE_WEATHER_INTEGRATION = True
ENABLE_GRAPH_GENERATION = True
ENABLE_BACKGROUND_EMAIL_PROCESSING = True
ENABLE_REMINDER_MONITORING = True
ENABLE_DEADLINE_TRACKING = True
