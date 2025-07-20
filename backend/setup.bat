@echo off
REM AI Personal Manager Setup Script for Windows

echo 🤖 AI Personal Manager - Secure Setup
echo =====================================

REM Check if .env.local exists
if exist ".env.local" (
    echo ⚠️  .env.local already exists. Do you want to overwrite it? (y/N)
    set /p choice="Enter y or n: "
    if /i not "%choice%"=="y" (
        echo Setup cancelled.
        exit /b 1
    )
)

REM Copy template files
echo 📋 Creating configuration files...
copy .env.example .env.local >nul
copy src\credentials.json.example src\credentials.json >nul

echo ✅ Template files created:
echo    - .env.local (copy of .env.example)
echo    - src\credentials.json (copy of credentials.json.example)

echo.
echo 🔧 Next Steps:
echo ==============
echo 1. Edit .env.local with your real API keys:
echo    - Get Google AI API key from: https://aistudio.google.com/
echo    - Get Mem0 API key from: https://mem0.ai/
echo    - Get OpenRouter API key from: https://openrouter.ai/
echo.
echo 2. Set up Gmail API credentials:
echo    - Go to: https://console.cloud.google.com/
echo    - Create OAuth2 credentials
echo    - Download and replace src\credentials.json
echo.
echo 3. Configure your database URL in .env.local
echo.
echo 4. Run the application:
echo    python app.py
echo.
echo 🔒 Security Reminder:
echo    - NEVER commit .env.local or src\credentials.json to git
echo    - These files contain your private credentials
echo.
echo 📖 For detailed setup instructions, see:
echo    - README.md
echo    - DEPLOYMENT.md
echo    - SECURITY.md

pause
