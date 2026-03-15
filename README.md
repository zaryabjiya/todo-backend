---
title: Phase 2 Backend
emoji: 🚀
colorFrom: blue
colorTo: gray
sdk: docker
port: 7860
app_file: main.py
pinned: false
---

# Todo App Backend

FastAPI backend for the Todo application.

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /users/{user_id}/tasks` - Get user tasks
- `POST /users/{user_id}/tasks` - Create task
- `PUT /users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /users/{user_id}/tasks/{task_id}` - Delete task

## API Documentation

Visit `/docs` for interactive API documentation.
