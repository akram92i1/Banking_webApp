# 🔐 Authentication Service

This microservice handles user authentication, registration, and token-based authorization for the Banking Platform.

## Features

- User registration and login
- Secure password hashing
- JWT (JSON Web Token) authentication
- User roles and permissions
- API endpoints for authentication workflows

## Tech Stack

- Node.js
- Express.js
- JWT for authentication
- bcrypt for password hashing
- PostgreSQL (or other DB) for user data

## Endpoints

- `POST /register` – Register a new user
- `POST /login` – Authenticate user and return JWT
- `GET /profile` – Get authenticated user profile (JWT required)

## Getting Started

1. Install dependencies:
   ```
   npm install
   ```
2. Set environment variables in a `.env` file (see `.env.example`).
3. Start the service:
   ```
   npm start
   ```

## Environment Variables

- `PORT` – Port to run the service
- `DATABASE_URL` – Connection string for the database
- `JWT_SECRET` – Secret key for signing JWTs

## License

MIT