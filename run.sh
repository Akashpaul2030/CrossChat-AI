#!/bin/bash

# Script to run the LangChain Assistant (backend and frontend)

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting LangChain Assistant...${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "TAVILY_API_KEY=your_tavily_api_key_here" >> .env
    echo -e "${RED}Please edit the .env file with your actual API keys before running again.${NC}"
    echo -e "${RED}Exiting...${NC}"
    exit 1
fi

# Check if API keys are set
if grep -q "your_openai_api_key_here" .env || grep -q "your_tavily_api_key_here" .env; then
    echo -e "${RED}Please edit the .env file with your actual API keys.${NC}"
    echo -e "${RED}Exiting...${NC}"
    exit 1
fi

# Create memory directory if it doesn't exist
mkdir -p memory

# Start the backend API server
echo -e "${GREEN}Starting backend API server...${NC}"
python -m src.api &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${YELLOW}Waiting for backend to start...${NC}"
sleep 5

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}Backend API server is running on http://localhost:8000${NC}"
else
    echo -e "${RED}Failed to start backend API server.${NC}"
    exit 1
fi

# Start the frontend development server
echo -e "${GREEN}Starting frontend development server...${NC}"
cd src/frontend && npm start

# Cleanup on exit
trap "kill $BACKEND_PID; echo -e '${YELLOW}Shutting down servers...${NC}'" EXIT
