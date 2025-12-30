#!/bin/bash
# Quick setup script for LLM Reliability Command Center

echo "🏥 LLM Reliability Command Center - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ⚠️  Virtual environment already exists"
fi

# Activate and install dependencies
echo ""
echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "   ✅ Dependencies installed"

# Create .env if it doesn't exist
echo ""
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Google Gemini API Key
# Get from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Datadog Configuration
# Get from: https://app.datadoghq.com/organization-settings/api-keys
DD_API_KEY=your_datadog_api_key_here
DD_APP_KEY=your_datadog_app_key_here
DD_SITE=datadoghq.com
DD_SERVICE=llm-reliability-command-center
DD_ENV=development

# Application Settings
BACKEND_URL=http://localhost:8000
FRONTEND_PORT=8501
EOF
    echo "   ✅ Created .env file"
    echo ""
    echo "   ⚠️  IMPORTANT: Edit .env and add your API keys!"
else
    echo "   ⚠️  .env file already exists"
fi

# Initialize RAG knowledge base
echo ""
echo "📚 Initializing RAG knowledge base..."
python3 -c "from rag import RAGEngine; rag = RAGEngine(); rag.load_sample_medical_docs(); print('   ✅ Sample documents loaded')"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Start backend:  python app.py"
echo "3. Start frontend: streamlit run frontend.py"
echo ""
echo "📚 See README.md for detailed instructions"
echo "=========================================="

