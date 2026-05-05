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

All endpoints are prefixed with `/api/`.

### Authentication

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| POST | `/api/register/` | No | Register new user, sends activation email |
| GET | `/api/activate/<uidb64>/<token>/` | No | Activate account via email link |
| POST | `/api/login/` | No | Login, sets JWT cookies |
| POST | `/api/logout/` | Yes | Logout, deletes JWT cookies |
| POST | `/api/token/refresh/` | No | Refresh access token via cookie |
| POST | `/api/password_reset/` | No | Send password reset email |
| POST | `/api/password_confirm/<uidb64>/<token>/` | No | Set new password |

### Videos

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| GET | `/api/video/` | Yes | List all videos |
| GET | `/api/video/<id>/<resolution>/index.m3u8` | Yes | HLS playlist for a resolution |
| GET | `/api/video/<id>/<resolution>/<segment>/` | Yes | HLS video segment |

**Available resolutions:** `480p`, `720p`, `1080p`

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
