# NetPulse Devices API

A small FastAPI project for managing network devices. Device reads are public; create, replace, update, and delete operations require a short-lived JWT bearer token. Device data is held in memory and resets when the server restarts.

## Requirements

- Python 3.9 or newer
- A terminal and a web browser

## Setup

Run these commands from this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set a local training username, password, and a random JWT secret of at least 32 characters. Keep `.env` private; it is excluded by `.gitignore` and must not be committed. You can generate a secret locally with:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

## Run

```bash
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000/docs> for interactive Swagger verification. Stop the server with `Ctrl+C`.

## API contract

| Method | Endpoint | Access | Success |
| --- | --- | --- | --- |
| POST | `/auth/token` | Public login | `200` with bearer token; `401` for invalid credentials |
| GET | `/devices` | Public | `200` |
| GET | `/devices/{device_id}` | Public | `200`; `404` if missing |
| POST | `/devices` | Bearer token required | `201`; `401` without a valid token |
| PUT | `/devices/{device_id}` | Bearer token required | `200`; `401` or `404` |
| PATCH | `/devices/{device_id}` | Bearer token required | `200`; `401` or `404` |
| DELETE | `/devices/{device_id}` | Bearer token required | `204`; `401` or `404` |

Device fields are `name`, `device_type`, `status`, and `location`. The API starts with two sample devices and assigns increasing integer IDs to new devices.

## Verify the flow in Swagger

1. Call `GET /devices` without authorization and confirm `200`.
2. Call `GET /devices/9999` and confirm `404`.
3. Call `POST /devices` without a token and confirm `401`.
4. Call `POST /auth/token` with an invalid username or password and confirm `401`.
5. In Swagger, click **Authorize** and enter the local username and password. Confirm that authorization succeeds; Swagger obtains the token from `/auth/token`.
6. Call `POST /devices` with a valid token and confirm `201`. Save the returned ID.
7. Call `GET /devices/{id}`, then `PUT` the device, then `PATCH` one field. Confirm `200` for each.
8. Call `DELETE /devices/{id}` and confirm `204`, then call `GET /devices/{id}` and confirm `404`.
9. Try an invalid bearer token on a protected endpoint and confirm `401`.
10. Repeat key public and protected checks in Postman. Do not include a full valid token in screenshots.

## Security notes

- Credentials and the JWT signing secret come from local environment settings, never from source code.
- The training password is hashed before use.
- Tokens use HS256 and include `sub` and `exp`; signature, expiry, and configured subject are checked.
- GET operations are public. POST, PUT, PATCH, and DELETE require a valid bearer token.
- This training API is for local use. Do not send bearer tokens over plain HTTP outside the local lab.

## Project scope

This is deliberately an in-memory beginner project: no database, external identity provider, registration, refresh tokens, roles, Docker, or cloud deployment.
