# Todo Backend API

This is the backend for the Todo Full-Stack Web Application (Phase II). It provides a secure REST API for managing user tasks with JWT-based authentication.

## Tech Stack

- Python 3.9+
- FastAPI
- SQLModel
- Better Auth
- Neon Serverless PostgreSQL
- PyJWT
- Uvicorn

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
BETTER_AUTH_SECRET=aPwV1FM8W5bmHF7o7xCgsq5PDACVaNFO
DATABASE_URL=postgresql://neondb_owner:npg_W5vTSROKo4ZJ@ep-small-base-a70deu8b-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

## Installation

1. Clone the repository
2. Navigate to the backend directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Authentication

Authentication is handled by Better Auth and available at `/api/auth/*`.

### Task Management

All task endpoints require JWT authentication in the Authorization header: `Authorization: Bearer <token>`

- `GET /api/{user_id}/tasks` - Get all tasks for the user
- `POST /api/{user_id}/tasks` - Create a new task
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle task completion status

### Query Parameters for GET /api/{user_id}/tasks

- `status` (optional): Filter by status - "all", "pending", "completed" (default: "all")
- `sort` (optional): Sort by - "created", "title", "due_date" (default: "created")

## Database Migrations

To run database migrations:

```bash
# Using Alembic (if configured)
alembic upgrade head
```

## Security Features

- JWT-based authentication
- User isolation (users can only access their own tasks)
- Input validation
- Proper error handling
- CORS configured for frontend origin (http://localhost:3000)

## Testing

To run tests:

```bash
pytest
```

## Frontend Integration

The backend is designed to work with a frontend at `http://localhost:3000`. The frontend should:

1. Authenticate users via `/api/auth/*` endpoints
2. Include JWT tokens in the Authorization header for task endpoints
3. Pass the authenticated user's ID in the URL path for task operations