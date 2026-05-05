# Videoflix Backend

A video streaming backend built with Django and Django REST Framework. Supports user registration with email activation, JWT authentication via HttpOnly cookies, and HLS video streaming in 480p, 720p, and 1080p.

---

## Setup

### Prerequisites

- **Docker Desktop** installed and running ([Installation](https://docs.docker.com/compose/install/))
- **Git** installed ([Installation](https://git-scm.com/downloads))

---

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd Backend
```

---

### Step 2 — Create the `.env` file

Copy the template file:

```bash
# Git Bash / macOS / Linux
cp .env.template .env

# Windows CMD
copy .env.template .env

# Windows PowerShell
Copy-Item .env.template .env
```

Open `.env` and fill in the required values:

```env
# Django admin superuser (created automatically on first start)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your_secure_password
DJANGO_SUPERUSER_EMAIL=your@email.com

# Django secret key — generate one at https://djecrety.ir/
SECRET_KEY="your-secret-key-here"

# Set to False in production
DEBUG=True

# Hosts allowed to access the backend
ALLOWED_HOSTS=localhost,127.0.0.1

# Frontend URL (for CORS and email links)
CORS_ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
FRONTEND_BASE_URL=http://127.0.0.1:5500

# PostgreSQL database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=your_db_password
DB_HOST=db
DB_PORT=5432

# Redis (leave as-is when using Docker)
REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

# Email (SMTP) — example for GMX
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.gmx.net
EMAIL_PORT=587
EMAIL_HOST_USER=your@gmx.de
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your@gmx.de
```

> **Note:** `DB_HOST=db` and `REDIS_HOST=redis` are the Docker service names — do not change these when running with Docker.
>
> **Email without SMTP:** To see emails in the terminal logs instead of sending them, set `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` in your `.env`.

---

### Step 3 — Start Docker

Build and start all containers (first time or after changes to `requirements.txt` or `Dockerfile`):

```bash
docker-compose up --build
```

For subsequent starts (no changes to dependencies):

```bash
docker-compose up
```

Docker starts three containers:

| Container | Description |
|---|---|
| `videoflix_backend` | Django + Gunicorn + RQ Worker |
| `videoflix_database` | PostgreSQL |
| `videoflix_redis` | Redis |

Migrations, static file collection and superuser creation run **automatically** on startup.

---

### Step 4 — Verify

Once you see this line in the logs, the backend is ready:

```
videoflix_backend | [INFO] Listening at: http://0.0.0.0:8000
```

- Backend API: [http://localhost:8000/api/](http://localhost:8000/api/)
- Django Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- RQ Dashboard: [http://localhost:8000/django-rq/](http://localhost:8000/django-rq/)

Login to the Admin with the credentials from `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` in your `.env`.

---

### Stop Docker

```bash
docker-compose down
```

> **Important:** Use `docker-compose down` followed by `docker-compose up` (not just `restart`) after changes to `.env`, so the new environment variables are loaded.

---

## Technology Stack

| Component | Technology |
|---|---|
| Backend Framework | Django 6.0.4 + Django REST Framework |
| Database | PostgreSQL |
| Cache & Task Queue | Redis + Django-RQ |
| Video Processing | FFmpeg (HLS Streaming) |
| Authentication | JWT in HttpOnly Cookies (djangorestframework-simplejwt) |
| Static Files | WhiteNoise |
| Server | Gunicorn |
| Containerization | Docker + Docker Compose |

---

## Features

- **User Registration** with email confirmation and account activation
- **JWT Authentication** stored in HttpOnly cookies (no localStorage)
- **Password Reset** via email link
- **HLS Video Streaming** in 480p, 720p, and 1080p
- **Background Processing** of video conversions via Redis Queue
- **Redis Caching** for improved performance
- **Django Admin** for content management

---

## Project Structure

```
Backend/
├── core/               # Django project settings and URL routing
├── accounts/           # User authentication (register, login, logout, password reset)
│   ├── models.py       # Custom User model (email-based, no username)
│   ├── views.py        # API endpoints
│   ├── serializers.py  # Request validation
│   ├── functions.py    # Business logic and email sending
│   ├── utils.py        # Helper functions
│   └── templates/      # Email HTML templates
├── videos/             # Video management and HLS streaming
│   ├── models.py       # Video model
│   ├── views.py        # API endpoints
│   ├── serializers.py  # Response data
│   ├── functions.py    # File path helpers
│   ├── tasks.py        # Background FFmpeg conversion
│   └── utils.py        # Segment name validation
├── requirements.txt
├── docker-compose.yml
├── backend.Dockerfile
└── backend.entrypoint.sh
```

---

## API Endpoints

Alle Endpunkte beginnen mit `/api/`.

---

### Authentifizierung

---

#### `POST /api/register/`

Erstellt ein neues Benutzerkonto und sendet eine Aktivierungs-E-Mail.

**Request Body**
```json
{
  "email": "string",
  "password": "string (min. 8 Zeichen)",
  "confirmed_password": "string"
}
```

**Success Response** `201 Created`
```json
{
  "user": { "id": 1, "email": "user@example.com" },
  "token": "string"
}
```

**Status Codes**
- `201` — Benutzer erfolgreich erstellt
- `400` — Passwörter stimmen nicht überein oder E-Mail bereits registriert

**Permissions:** Keine

---

#### `GET /api/activate/<uidb64>/<token>/`

Aktiviert ein Benutzerkonto anhand der uidb64 und des Tokens aus der Aktivierungs-E-Mail.

**URL Parameter**

| Name | Beschreibung |
|---|---|
| `uidb64` | Base64-kodierte User-ID (aus dem E-Mail-Link) |
| `token` | Aktivierungstoken (aus dem E-Mail-Link) |

**Request Body:** keiner

**Success Response** `200 OK`
```json
{ "message": "Account successfully activated." }
```

**Status Codes**
- `200` — Konto erfolgreich aktiviert
- `400` — Token ungültig oder abgelaufen

**Permissions:** Keine

---

#### `POST /api/login/`

Meldet den Benutzer an und setzt JWT-Tokens als HttpOnly-Cookies.

**Request Body**
```json
{
  "email": "string",
  "password": "string"
}
```

**Success Response** `200 OK`
```json
{
  "detail": "Login successful",
  "user": { "id": 1, "username": "user@example.com" }
}
```
> Setzt `access_token` und `refresh_token` als HttpOnly-Cookies.

**Status Codes**
- `200` — Login erfolgreich
- `400` — Ungültige Zugangsdaten oder Konto nicht aktiviert

**Permissions:** Keine

---

#### `POST /api/logout/`

Meldet den Benutzer ab, setzt den Refresh-Token auf die Blacklist und löscht alle Cookies.

**Request Body:** keiner (Refresh-Token wird aus dem Cookie gelesen)

**Success Response** `200 OK`
```json
{ "detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid." }
```

**Status Codes**
- `200` — Logout erfolgreich
- `400` — Refresh-Token fehlt oder ungültig

**Permissions:** Keine (Token wird automatisch aus dem Cookie gelesen)

---

#### `POST /api/token/refresh/`

Gibt einen neuen Access-Token aus, wenn das Refresh-Token-Cookie noch gültig ist.

**Request Body:** keiner (Refresh-Token wird aus dem Cookie gelesen)

**Success Response** `200 OK`
```json
{
  "detail": "Token refreshed",
  "access": "string"
}
```

**Status Codes**
- `200` — Access-Token erfolgreich erneuert
- `400` — Refresh-Token fehlt
- `401` — Refresh-Token ungültig oder abgelaufen

**Permissions:** Keine

---

#### `POST /api/password_reset/`

Sendet eine Passwort-Reset-E-Mail, wenn ein Konto mit der angegebenen E-Mail existiert.

**Request Body**
```json
{ "email": "string" }
```

**Success Response** `200 OK`
```json
{ "detail": "An email has been sent to reset your password." }
```

> Gibt immer `200` zurück, auch wenn die E-Mail nicht existiert (Sicherheitsgründe).

**Status Codes**
- `200` — Anfrage entgegengenommen

**Permissions:** Keine

---

#### `POST /api/password_confirm/<uidb64>/<token>/`

Setzt ein neues Passwort anhand der uidb64 und des Tokens aus der Reset-E-Mail.

**URL Parameter**

| Name | Beschreibung |
|---|---|
| `uidb64` | Base64-kodierte User-ID (aus dem E-Mail-Link) |
| `token` | Reset-Token (aus dem E-Mail-Link) |

**Request Body**
```json
{
  "new_password": "string",
  "confirm_password": "string"
}
```

**Success Response** `200 OK`
```json
{ "detail": "string" }
```

**Status Codes**
- `200` — Passwort erfolgreich geändert
- `400` — Token ungültig oder Passwörter stimmen nicht überein

**Permissions:** Keine

---

### Videos

---

#### `GET /api/video/`

Gibt eine Liste aller verfügbaren Videos mit Metadaten zurück.

**Request Body:** keiner

**Success Response** `200 OK`
```json
[
  {
    "id": 1,
    "created_at": "2026-01-01T00:00:00Z",
    "title": "string",
    "description": "string",
    "thumbnail_url": "string",
    "category": "string"
  }
]
```

**Status Codes**
- `200` — Liste erfolgreich zurückgegeben
- `401` — Nicht authentifiziert

**Permissions:** JWT-Authentifizierung erforderlich

---

#### `GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8`

Gibt die HLS-Master-Playlist für einen bestimmten Film und eine gewählte Auflösung zurück.

**URL Parameter**

| Name | Beschreibung |
|---|---|
| `movie_id` | Die ID des Films |
| `resolution` | Gewünschte Auflösung (`480p`, `720p`, `1080p`) |

**Request Body:** keiner

**Success Response** `200 OK`

HLS-Manifestdatei (`Content-Type: application/vnd.apple.mpegurl`)

**Status Codes**
- `200` — Manifest erfolgreich geliefert
- `404` — Video oder Manifest nicht gefunden

**Rate Limits:** Keine

**Permissions:** JWT-Authentifizierung erforderlich

---

#### `GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>/`

Gibt ein einzelnes HLS-Videosegment (`.ts`-Datei) für einen Film und eine Auflösung zurück.

**URL Parameter**

| Name | Beschreibung |
|---|---|
| `movie_id` | Die ID des Films |
| `resolution` | Gewünschte Auflösung (`480p`, `720p`, `1080p`) |
| `segment` | Segmentname (z.B. `segment0.ts`) |

**Request Body:** keiner

**Success Response** `200 OK`

Videosegment (`Content-Type: video/MP2T`)

**Status Codes**
- `200` — Segment erfolgreich geliefert
- `404` — Segment nicht gefunden

**Rate Limits:** Keine

**Permissions:** JWT-Authentifizierung erforderlich

---

## Configuration

### Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | Debug mode (`True`/`False`) | No (default: `True`) |
| `ALLOWED_HOSTS` | Allowed hosts, comma-separated | Yes |
| `CORS_ALLOWED_ORIGINS` | Frontend origins, comma-separated | Yes |
| `CSRF_TRUSTED_ORIGINS` | CSRF trusted origins | Yes |
| `FRONTEND_BASE_URL` | Base URL of the frontend | Yes |
| `DB_NAME` | PostgreSQL database name | Yes |
| `DB_USER` | PostgreSQL user | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_HOST` | Database host (default: `db`) | No |
| `DB_PORT` | Database port (default: `5432`) | No |
| `REDIS_HOST` | Redis host (default: `redis`) | No |
| `REDIS_PORT` | Redis port (default: `6379`) | No |
| `REDIS_LOCATION` | Full Redis URL | No |
| `EMAIL_BACKEND` | Django email backend class | No |
| `EMAIL_HOST` | SMTP server address | Yes (for email) |
| `EMAIL_PORT` | SMTP port (default: `587`) | No |
| `EMAIL_HOST_USER` | SMTP username / sender address | Yes (for email) |
| `EMAIL_HOST_PASSWORD` | SMTP password | Yes (for email) |
| `EMAIL_USE_TLS` | Use TLS (`True`/`False`) | No (default: `False`) |
| `EMAIL_USE_SSL` | Use SSL (`True`/`False`) | No (default: `False`) |
| `DEFAULT_FROM_EMAIL` | Sender display address | No |
| `DJANGO_SUPERUSER_EMAIL` | Auto-created admin email | No |
| `DJANGO_SUPERUSER_PASSWORD` | Auto-created admin password | No |
| `JWT_COOKIE_SECURE` | HTTPS-only cookies | No (default: `False`) |
| `JWT_COOKIE_SAMESITE` | SameSite cookie policy | No (default: `Lax`) |

> **For production:** Set `DEBUG=False`, use a strong `SECRET_KEY`, configure HTTPS URLs in `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`, and set `JWT_COOKIE_SECURE=True`.

---

## Usage

### Admin Panel

Access the Django Admin at [http://localhost:8000/admin](http://localhost:8000/admin)

Credentials from `.env`:
- Email: `DJANGO_SUPERUSER_EMAIL`
- Password: `DJANGO_SUPERUSER_PASSWORD`

### Upload Videos

1. Login to Admin Panel
2. Go to **Videos** → **Add Video**
3. Fill in title, description, category, and thumbnail, upload video file
4. Save — FFmpeg conversion starts automatically in the background
5. Monitor progress at [http://localhost:8000/django-rq/](http://localhost:8000/django-rq/)

### Run Migrations Manually

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### Add Python Packages

1. Add the package to `requirements.txt`
2. Rebuild the container:
   ```bash
   docker compose up --build
   ```

---

## Troubleshooting

### Entrypoint script error

**Error:** `exec ./backend.entrypoint.sh: no such file or directory`

**Solution:** The file has Windows line endings (CRLF). Convert to LF:
- In VS Code: click `CRLF` in the bottom-right status bar → select `LF`, then save

### Port 8000 already in use

**Error:** `port is already allocated`

**Solution:** Stop the conflicting process or change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"
```

### Docker won't start

**Error:** `unable to get image 'postgres:latest'`

**Solution:** Make sure Docker Desktop is running.

### Migration fails after model changes

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

---

## License

This project is licensed under the MIT License.
