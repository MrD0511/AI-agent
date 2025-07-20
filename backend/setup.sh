#!/bin/bash
# AI Personal Manager Setup Script

echo "🤖 AI Personal Manager - Secure Setup"
echo "====================================="

# Check if .env.local exists
if [ -f ".env.local" ]; then
    echo "⚠️  .env.local already exists. Do you want to overwrite it? (y/N)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Copy template files
echo "📋 Creating configuration files..."
cp .env.example .env.local
cp src/credentials.json.example src/credentials.json

echo "✅ Template files created:"
echo "   - .env.local (copy of .env.example)"  
echo "   - src/credentials.json (copy of credentials.json.example)"

echo ""
echo "🔧 Next Steps:"
echo "=============="
echo "1. Edit .env.local with your real API keys:"
echo "   - Get Google AI API key from: https://aistudio.google.com/"
echo "   - Get Mem0 API key from: https://mem0.ai/"
echo "   - Get OpenRouter API key from: https://openrouter.ai/"
echo ""
echo "2. Set up Gmail API credentials:"
echo "   - Go to: https://console.cloud.google.com/"
echo "   - Create OAuth2 credentials"
echo "   - Download and replace src/credentials.json"
echo ""
echo "3. Configure your database URL in .env.local"
echo ""
echo "4. Run the application:"
echo "   python app.py"
echo ""
echo "🔒 Security Reminder:"
echo "   - NEVER commit .env.local or src/credentials.json to git"
echo "   - These files contain your private credentials"
echo ""
echo "📖 For detailed setup instructions, see:"
echo "   - README.md"
echo "   - DEPLOYMENT.md" 
echo "   - SECURITY.md"
