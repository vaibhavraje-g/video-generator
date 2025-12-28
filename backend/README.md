# Video Generator Backend

Full-stack video generation platform with JWT authentication, MongoDB integration, and project management.

## Features

- 🔐 JWT-based authentication (register, login, token refresh)
- 📁 Project management with user isolation
- 🎬 Async video generation with status tracking
- 📊 Video history and metadata storage
- 🧪 Comprehensive test suite (unit + integration)
- 📝 Auto-generated API documentation (Swagger)

## Requirements

- Python 3.9+
- MongoDB 4.4+
- FFmpeg (for video processing)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the backend directory:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=video_generator

# Security (change in production!)
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys
GEMINI_API_KEY=your_gemini_api_key
PIXABAY_API_KEY=your_pixabay_api_key

# Server
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 3. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install MongoDB locally
mongod --dbpath /path/to/data
```

### 4. Run the Server

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routes/        # API route handlers
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── db/
│   │   └── mongodb.py         # Database connection
│   ├── middleware/
│   │   └── auth.py            # JWT authentication
│   ├── models/                # Pydantic models
│   ├── services/              # Business logic
│   ├── utils/                 # Security utilities
│   └── main.py                # FastAPI app
├── tests/
│   ├── unit/                  # Unit tests
│   └── integration/           # Integration tests
├── docs/
│   └── frontend_requirements.md
└── requirements.txt
```

## Key API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `GET /api/v1/auth/me` - Get current user info

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects` - List user's projects
- `GET /api/v1/projects/{id}` - Get project details
- `DELETE /api/v1/projects/{id}` - Delete project
- `GET /api/v1/projects/{id}/history` - Get video history

### Videos
- `POST /api/v1/videos/generate` - Generate video (async)
- `GET /api/v1/videos/{id}` - Get video status/details

## Development

### Code Style

Follow PEP 8 guidelines. Use black for formatting:

```bash
pip install black
black app/ tests/
```

### Adding New Features

1. Create models in `app/models/`
2. Implement business logic in `app/services/`
3. Add routes in `app/api/v1/routes/`
4. Write tests in `tests/`

## Deployment

See `docs/deployment.md` for production deployment guidelines.

## License

MIT
