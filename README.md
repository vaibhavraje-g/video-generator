# Video Generator - Full Stack Application

A full-stack video generation platform with authentication, project management, and AI-powered Family Guy style educational videos.

## Structure

```
video-generator/
├── backend/           # FastAPI backend with MongoDB
│   ├── app/          # Application code
│   ├── tests/        # Test suite
│   └── docs/         # Documentation
├── frontend/         # Frontend application (to be added)
├── assets/           # Shared assets (characters, videos)
└── README.md         # This file
```

## Quick Start

### Prerequisites

- Python 3.9+
- MongoDB 4.4+
- Node.js 16+ (for frontend)
- FFmpeg

### Backend Setup

See [backend/README.md](backend/README.md) for detailed instructions.

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
# Instructions to be added once frontend is implemented
```

## Features

### Backend
- ✅ JWT authentication (login/register)
- ✅ MongoDB with async Motor driver
- ✅ Project management with user isolation
- ✅ Video generation with status tracking
- ✅ Comprehensive test suite
- ✅ API documentation (Swagger/OpenAPI)

### Frontend (To be implemented)
- Login/Register pages
- Dashboard with projects
- Project detail with video history
- Video generation form
- Video player

## Documentation

- [Backend API Documentation](backend/docs/frontend_requirements.md)
- [Implementation Plan](.gemini/antigravity/brain/c602a646-fcb4-4e10-b303-d7b3a1b8ff3b/implementation_plan.md)

## Architecture

**Backend**: FastAPI + MongoDB
- RESTful API with JWT auth
- Async video generation
- Background task processing

**Frontend**: (Your choice - React/Vue/Angular recommended)
- See `backend/docs/frontend_requirements.md` for detailed UI specs

**Database**: MongoDB
- Users collection
- Projects collection
- Videos collection

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT