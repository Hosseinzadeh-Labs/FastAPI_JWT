# FastAPI JWT Authentication

A practical FastAPI authentication project that implements:
- Access token + refresh token flow
- Refresh token rotation and token reuse detection
- Cookie-based auth for browser clients
- CSRF token protection for sensitive requests
- Logout and session invalidation behavior

This project is designed as a learning-focused backend reference for secure JWT handling with FastAPI.

## Tech Stack
- Python
- FastAPI
- python-jose (JWT)
- Uvicorn

## Project Structure
```text
.
├── main.py
├── requirements.txt
└── README.md
```

## Run Locally
1. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the API server:
```bash
uvicorn main:app --reload
```

Server runs at: `http://127.0.0.1:8000`

## API Endpoints
- `GET /login-local`
Creates and sets:
`access_token`, `refresh_token`, and `csrf_token` cookies.

- `GET /profile_local`
Reads and validates `access_token` from cookies.

- `GET /refresh`
Validates refresh token, rotates it, and issues a new access token.

- `POST /update_profile`
Checks CSRF by comparing:
cookie `csrf_token` and header `X-CSRF-Token`.

- `GET /logout_local`
Invalidates current refresh token and clears auth cookies.

## Security Notes
- Access tokens are short-lived (`5 minutes`).
- Refresh tokens are long-lived (`7 days`) and rotated on use.
- Token reuse detection revokes sessions for the user.
- CSRF protection is applied for state-changing requests.

## Resume Highlights
- Implemented end-to-end JWT auth flow in FastAPI.
- Added refresh token rotation with replay/reuse mitigation.
- Used cookie-based auth and CSRF verification for browser safety.
- Built clear, testable auth endpoints for real-world backend patterns.
