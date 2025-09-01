#!/bin/bash

echo "🚀 Setting up AI Medical Insurance Coverage Checker..."

# Check if .env file already exists
if [ -f "backend/.env" ]; then
    echo "⚠️  backend/.env already exists. Skipping creation."
    echo "If you need to update API keys, please edit backend/.env manually."
else
    echo "📝 Creating backend/.env file..."
    
    # Create the .env file with placeholder values
    cat > backend/.env << 'EOF'
# Add your actual API keys here:
OPENAI_API_KEY=sk-your-openai-api-key-here
PINECONE_API_KEY=pcn-your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=docsage-lite
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/docsage
TESSERACT_CMD=/usr/bin/tesseract
EOF

    echo "✅ backend/.env file created!"
    echo ""
    echo "🔑 IMPORTANT: Please edit backend/.env and add your actual API keys:"
    echo "   - Get OpenAI API key from: https://platform.openai.com/"
    echo "   - Get Pinecone API key from: https://pinecone.io/"
    echo ""
    echo "📝 Edit the file with: nano backend/.env"
fi

echo ""
echo "🐳 Starting the application..."
echo "   This will build and start all Docker containers."
echo ""

# Start the application
docker compose up --build -d

echo ""
echo "🎉 Setup complete!"
echo "🌐 Access your app at: http://localhost:8502"
echo "🔧 Backend API at: http://localhost:8001"
echo ""
echo "📋 To stop the app: docker compose down"
echo "📋 To view logs: docker compose logs"
