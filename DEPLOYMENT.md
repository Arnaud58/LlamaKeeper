# AI Dungeon Clone - Deployment Guide

## Prerequisites

### System Requirements
- Python 3.9+
- pip
- keeper
- Ollama (local AI model server)

### Supported Platforms
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, Fedora 33+)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/Arnaud58/LlamaKeeper.git
cd LlamaKeeper
```

### 2. Create Virtual Environment
```bash
conda create --name keeper python=3.13
conda activate keeper
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Install Ollama
#### Windows
1. Download from [ollama.ai](https://ollama.ai/download)
2. Run the installer
3. Restart terminal

#### macOS
```bash
curl https://ollama.ai/install.sh | sh
```

#### Linux
```bash
curl https://ollama.ai/install.sh | sh
```

### 5. Pull Required Models
```bash
ollama pull llama2:7b
ollama pull mistral:7b
```

### 6. Database Setup
```bash
# Run database migrations
cd backend
python run_migrations.py
```

### 7. Configure Environment
Create a `.env` file in the `backend` directory:
```
DATABASE_URL=sqlite:///./ai_dungeon.db
OLLAMA_BASE_URL=http://localhost:11434/api
LOG_LEVEL=INFO
```

### 8. Run the Application
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# In a separate terminal, start frontend
python -m http.server 8000 --directory ../frontend
```

### 9. Access the Application
Open a web browser:
- Backend: `http://localhost:8000/`
- Frontend: `http://localhost:8000`

## Deployment Modes

### Development Mode
- Uses SQLite database
- Local Ollama server
- Hot reloading enabled

### Production Mode
#### Recommended Configurations
- PostgreSQL database
- Gunicorn/Uvicorn for ASGI server
- Nginx as reverse proxy
- Docker containerization

#### Production Deployment Script
```bash
# Example production startup
gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    app.main:app
```

## Monitoring

### Logging
- Logs stored in `backend/app.log`
- Configurable log levels in `.env`

### Performance Metrics
- Request performance tracked
- Error logging with detailed context

## Troubleshooting

### Common Issues
1. **Ollama Not Running**
   - Ensure Ollama service is started
   - Check Ollama logs

2. **Model Download Failures**
   - Verify internet connection
   - Manually pull models using `ollama pull`

3. **Database Connection**
   - Check database path
   - Ensure migrations are applied

## Security Considerations
- Use HTTPS in production
- Set strong database credentials
- Implement proper authentication
- Regularly update dependencies

## Scaling Recommendations
- Use connection pooling
- Implement caching
- Consider distributed model serving

## Backup and Maintenance
- Regularly backup SQLite database
- Update Ollama models periodically
- Monitor system resources