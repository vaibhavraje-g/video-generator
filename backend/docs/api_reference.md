# Video Generator API Reference

Base URL: `http://localhost:8000/api/v1`

## Authentication

All endpoints except `/auth/register` and `/auth/login` require Bearer token authentication.

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user |
| POST | `/auth/login` | Get access token |
| GET | `/auth/me` | Get current user |

#### POST /auth/register

```json
// Request
{
  "email": "user@example.com",
  "username": "user123",
  "password": "securepassword"
}

// Response 201
{
  "_id": "...",
  "email": "user@example.com",
  "username": "user123",
  "is_active": true,
  "created_at": "2024-12-28T..."
}
```

#### POST /auth/login

```json
// Request
{
  "email": "user@example.com",
  "password": "securepassword"
}

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Generators

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/generators` | List available generators |
| GET | `/generators/{id}` | Get generator details |
| GET | `/generators/{id}/schema` | Get config schema |

#### GET /generators

```json
// Response 200
[
  {
    "id": "family_guy",
    "display_name": "Explainer (Family Guy)",
    "description": "Short comedy explainer videos...",
    "supported_durations": ["short"],
    "config_schema": { ... }
  },
  {
    "id": "frequency",
    "display_name": "Frequency/Healing",
    "description": "Healing videos with solfeggio frequencies...",
    "supported_durations": ["short", "long"],
    "config_schema": { ... }
  },
  {
    "id": "subliminal",
    "display_name": "Subliminal",
    "description": "Subliminal affirmation videos...",
    "supported_durations": ["short", "long"],
    "config_schema": { ... }
  }
]
```

---

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List user's projects |
| POST | `/projects` | Create project |
| GET | `/projects/{id}` | Get project |
| DELETE | `/projects/{id}` | Delete project |
| GET | `/projects/{id}/history` | Get video history |

---

### Videos

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/videos/generate` | Start video generation |
| GET | `/videos/{id}` | Get video status |

#### POST /videos/generate

```json
// Request
{
  "project_id": "...",
  "generator_id": "frequency",
  "topic": "Abundance and prosperity",
  
  // Common config
  "aspect_ratio": "9:16",  // "9:16" | "1:1" | "16:9"
  "duration": "short",     // "short" | "long"
  "output_format": "mp4",  // "mp4" | "webm" | "mov"
  "quality": "1080p",      // "720p" | "1080p" | "4k"
  
  // Generator-specific config
  "generator_config": {
    "frequency": 528,
    "visual_style": "sacred_geometry",
    "include_binaural": true
  }
}

// Response 202
{
  "_id": "...",
  "project_id": "...",
  "user_id": "...",
  "topic": "Abundance and prosperity",
  "generator_id": "frequency",
  "status": "pending",
  "progress": 0,
  "current_step": "Queued",
  "created_at": "2024-12-28T..."
}
```

#### GET /videos/{id}

```json
// Response 200 (processing)
{
  "_id": "...",
  "status": "processing",
  "progress": 45.5,
  "current_step": "Generating audio",
  ...
}

// Response 200 (completed)
{
  "_id": "...",
  "status": "completed",
  "progress": 100,
  "video_url": "/static/frequency_abc123.mp4",
  "metadata": {
    "duration_seconds": 60,
    "file_size_bytes": 15728640
  },
  ...
}
```

---

## Generator Config Schemas

### family_guy

```json
{
  "style": "family_guy",      // only option
  "background": "gaming"      // "gaming" | "abstract" | "custom"
}
```

### frequency

```json
{
  "frequency": 528,                    // 432 | 528 | 639 | 741 | 852 | 963
  "visual_style": "sacred_geometry",   // sacred_geometry | nature | waves | mandala | particles | minimal
  "affirmation_theme": "abundance",    // custom theme
  "include_binaural": false,           // add binaural beats
  "text_overlay": true                 // show affirmations on screen
}
```

### subliminal

```json
{
  "category": "wealth",               // wealth | confidence | health | relationships | success | custom
  "technique": "flash_text",          // flash_text | background_blend | audio_layered | mirror_reverse
  "background_style": "nature",       // nature | abstract | space | ocean | custom
  "audio_track": "ambient",           // ambient | binaural | nature | lofi | custom
  "custom_affirmations": []           // optional custom list
}
```

---

## Status Values

| Status | Description |
|--------|-------------|
| `pending` | Queued for processing |
| `processing` | Currently generating |
| `completed` | Video ready |
| `failed` | Generation failed |

---

## Error Responses

```json
// 400 Bad Request
{
  "detail": "Generator 'unknown' not found. Available: ['family_guy', 'frequency', 'subliminal']"
}

// 401 Unauthorized
{
  "detail": "Not authenticated"
}

// 404 Not Found
{
  "detail": "Video not found"
}
```
