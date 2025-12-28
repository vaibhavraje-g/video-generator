# Frontend Requirements Document

> **Auto-generated API documentation is available at `/docs` (Swagger UI) when the backend is running.**

## Overview

This document provides comprehensive requirements for building the frontend UI for the Video Generator platform. The backend provides a RESTful API with JWT authentication, project management, and video generation capabilities.

## Technology Stack Recommendations

- **Framework**: React, Vue.js, or Angular
- **State Management**: Redux, Vuex, or NgRx
- **HTTP Client**: Axios or Fetch API
- **Routing**: React Router, Vue Router, or Angular Router
- **UI Components**: Material-UI, Ant Design, or custom components

---

## Authentication

### Login Page

**Route**: `/login`

**Features**:
- Email and password input fields
- "Remember me" checkbox (optional)
- Login button
- Link to registration page
- Error message display for invalid credentials

**API Endpoint**: `POST /api/v1/auth/login`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Handling**:
- 401: Display "Invalid email or password"
- Network errors: Display "Unable to connect to server"

---

### Registration Page

**Route**: `/register`

**Features**:
- Email input with validation
- Username input
- Password input with strength indicator
- Confirm password field
- Register button
- Link to login page
- Success message on registration

**API Endpoint**: `POST /api/v1/auth/register`

**Request**:
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "securepassword123"
}
```

**Response**:
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "email": "newuser@example.com",
  "username": "newuser",
  "is_active": true,
  "created_at": "2025-12-03T08:00:00Z"
}
```

**Error Handling**:
- 400 with "Email already registered": Display error under email field
- 400 with "Username already taken": Display error under username field
- Validation errors: Display inline field errors

---

## Dashboard

### Projects Overview

**Route**: `/dashboard`

**Features**:
- List of user's projects with cards/table
- Each project shows: name, description, creation date, video count
- "Create New Project" button
- Search/filter projects (client-side or server-side)
- Pagination controls
- Click on project to view details

**API Endpoint**: `GET /api/v1/projects?skip=0&limit=20`

**Headers**:
```
Authorization: Bearer {access_token}
```

**Response**:
```json
[
  {
    "_id": "507f1f77bcf86cd799439011",
    "user_id": "507f1f77bcf86cd799439012",
    "name": "AI Explainer Videos",
    "description": "Educational videos about AI concepts",
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-01T10:00:00Z"
  }
]
```

---

### Create Project Modal

**Features**:
- Modal/dialog triggered by "Create New Project" button
- Project name input (required)
- Project description textarea (optional)
- Cancel and Create buttons

**API Endpoint**: `POST /api/v1/projects`

**Request**:
```json
{
  "name": "My New Project",
  "description": "Project description here"
}
```

---

## Project Detail Page

**Route**: `/projects/:projectId`

**Features**:
- Project header with name, description, edit/delete buttons
- Video generation form
- Video history table/list

**API Endpoint**: `GET /api/v1/projects/:projectId`

---

### Video Generation Form

**Features**:
- Topic input field (required)
- Video type dropdown (currently only "Family Guy")
- Generate button
- Loading spinner during generation
- Success/error notifications

**API Endpoint**: `POST /api/v1/videos/generate`

**Request**:
```json
{
  "project_id": "507f1f77bcf86cd799439011",
  "topic": "How Neural Networks Work",
  "video_type": "family_guy"
}
```

**Response** (202 Accepted):
```json
{
  "_id": "507f1f77bcf86cd799439013",
  "project_id": "507f1f77bcf86cd799439011",
  "user_id": "507f1f77bcf86cd799439012",
  "topic": "How Neural Networks Work",
  "video_type": "family_guy",
  "status": "pending",
  "video_url": null,
  "created_at": "2025-12-03T08:30:00Z"
}
```

**Polling**:
- Poll `GET /api/v1/videos/:videoId` every 5 seconds to check status
- Update UI when status changes from "pending" → "processing" → "completed"

---

### Video History

**Features**:
- Table/list showing all videos in the project
- Columns: Topic, Status, Created Date, Actions
- Status badge with color coding:
  - Pending: Yellow/Orange
  - Processing: Blue
  - Completed: Green
  - Failed: Red
- View/Download button for completed videos
- Error message display for failed videos

**API Endpoint**: `GET /api/v1/projects/:projectId/history`

**Response**:
```json
{
  "videos": [
    {
      "_id": "507f1f77bcf86cd799439013",
      "topic": "How Neural Networks Work",
      "status": "completed",
      "video_url": "/static/output_abc123.mp4",
      "created_at": "2025-12-03T08:30:00Z",
      "completed_at": "2025-12-03T08:35:00Z"
    }
  ]
}
```

---

## Video Player

**Route**: `/videos/:videoId` or Modal

**Features**:
- Embedded HTML5 video player
- Video controls (play, pause, volume, fullscreen)
- Download button
- Video metadata display (topic, creation date)

**API Endpoint**: `GET /api/v1/videos/:videoId`

**Video URL**: The `video_url` field from the response (e.g., `/static/output_abc123.mp4`)

---

## State Management

### Auth State

Store in localStorage or sessionStorage:
```javascript
{
  accessToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  refreshToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  user: {
    id: "507f1f77bcf86cd799439012",
    email: "user@example.com",
    username: "user123"
  }
}
```

### Request Interceptor

Add Authorization header to all API requests:
```javascript
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Token Refresh

- Monitor for 401 responses
- When access token expires, use refresh token to get new access token
- Logout user if refresh token also expires

---

## Error Handling

### Common Error Responses

**401 Unauthorized**:
- Redirect to login page
- Clear stored tokens

**403 Forbidden**:
- Display "You don't have permission to access this resource"

**404 Not Found**:
- Display "Resource not found" message
- For projects: redirect to dashboard
- For videos: show error in video list

**500 Internal Server Error**:
- Display "Something went wrong. Please try again later."
- Show retry button

---

## UI/UX Guidelines

### Navigation

- Top navbar with:
  - Logo/app name
  - Dashboard link
  - User menu (profile, logout)
- Sidebar (optional):
  - Projects list
  - Quick actions

### Responsive Design

- Mobile-first approach
- Tablet and desktop optimizations
- Collapsible sidebar on mobile

### Loading States

- Skeleton loaders for content
- Spinner for actions (generation, deletion)
- Progress indicators for long operations

### Notifications

- Toast notifications for:
  - Successful actions (project created, video generated)
  - Errors
  - Video status updates
- Auto-dismiss after 5 seconds (except errors)

---

## API Base URL

Development: `http://localhost:8000`  
Production: Configure via environment variables

---

## Sample API Usage

### Complete Login Flow

```javascript
// Login
const loginResponse = await axios.post('/api/v1/auth/login', {
  email: 'user@example.com',
  password: 'password123'
});

// Store tokens
localStorage.setItem('accessToken', loginResponse.data.access_token);
localStorage.setItem('refreshToken', loginResponse.data.refresh_token);

// Get user info
const userResponse = await axios.get('/api/v1/auth/me', {
  headers: {
    Authorization: `Bearer ${loginResponse.data.access_token}`
  }
});
```

### Video Generation with Polling

```javascript
// Start generation
const generateResponse = await axios.post('/api/v1/videos/generate', {
  project_id: projectId,
  topic: 'Quantum Computing',
  video_type: 'family_guy'
});

const videoId = generateResponse.data._id;

// Poll for status
const pollInterval = setInterval(async () => {
  const statusResponse = await axios.get(`/api/v1/videos/${videoId}`);
  
  if (statusResponse.data.status === 'completed') {
    clearInterval(pollInterval);
    // Show success notification
    // Display video player
  } else if (statusResponse.data.status === 'failed') {
    clearInterval(pollInterval);
    // Show error notification
  }
}, 5000);
```

---

## Testing Checklist

- [ ] User can register with valid credentials
- [ ] Registration fails with duplicate email/username
- [ ] User can login with valid credentials
- [ ] Login fails with wrong password
- [ ] Protected routes redirect to login when not authenticated
- [ ] User can create a new project
- [ ] User can view their projects list
- [ ] User can delete a project
- [ ] User can generate a video
- [ ] Video status updates in real-time
- [ ] Completed video can be viewed/downloaded
- [ ] Failed video shows error message
- [ ] User cannot access other users' projects/videos
- [ ] Token refresh works correctly
- [ ] Logout clears tokens and redirects to login
