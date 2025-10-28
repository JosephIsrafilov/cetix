Cetix

Habr-inspired Django platform for publishing curated engineering articles with moderation workflow, role-based permissions, comments, reactions, bookmarks, and a sleek Reddit-esque dark theme.

Site Overall
-----------

-   Home feed with spotlight hero and stat chips
-   Article detail with reactions/bookmarks and threaded comments
-   Category and author hubs with gradient cards

Requirements
------------

-   Python 3.12
-   pip / virtualenv
-   SQLite (bundled) -- or configure your own database via `DATABASES`

Quick Start
-----------

1.  **Clone the repository**

        git clone https://github.com/JosephIsrafilov/cetix.git
        cd cetix

2.  **Create and activate a virtual environment**

        python -m venv .venv
        # Windows PowerShell
        .\.venv\Scripts\Activate.ps1
        # macOS/Linux
        source .venv/bin/activate

3.  **Install dependencies**

        pip install --upgrade pip
        pip install -r requirements.txt

4.  **Apply migrations and seed demo data**

        python manage.py migrate
        python manage.py seed_demo_content --flush-existing  #sample data for project

5.  **Create a superuser (optional but useful)**

        python manage.py createsuperuser

6.  **Run the development server**

        python manage.py runserver
        # or ASGI/FastAPI-style entry via Uvicorn:
        python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

7.  **Open the site**

        http://127.0.0.1:8000/

Project Structure
-----------------

-   `accounts/` â€“ custom user model, roles, profiles, auth forms, password reset.
-   `articles/`
    -   `models.py` â€“ Category, Article, reactions, bookmarks, comments.
    -   `views.py` â€“ Feed, detail, category/author listings, moderation, bookmarks.
    -   `forms.py` â€“ Article creation with moderation awareness, comment form.
    -   `management/commands/seed_demo_content.py` â€“ Demo seed script (covers, comments, reactions, bookmarks).
-   `templates/` â€“ Dark themed UI with shared `page_hero` include and React-style interactions using vanilla JS.
-   `static/css/style.css` â€“ Reddit-inspired styling, gradients, hero themes.
-   `static/js/`
    -   `password-toggle.js` â€“ toggles password visibility.
    -   `reactions.js` â€“ optimistic like/dislike updates with fetch + session storage.
    -   `comments.js` / `layout.js` â€“ comment interactions, profile dropdown.
-   `main.py` â€“ ASGI entrypoint for Uvicorn.
-   `config/` â€“ Project settings/urls.
-   `requirements.txt` â€“ Django, Pillow, Requests, Uvicorn (standard), WhiteNoise.

Feature Overview
----------------

-   **Roles**: guest, user, admin, super admin. Admins moderate content, ban users, manage roles.
-   **Moderation**: user-submitted articles require admin approval; admins access `/articles/moderation_queue/`.
-   **Bookmarks & Reactions**: likes/dislikes with optimistic UI updates; personal bookmark list.
-   **Comments**: threaded replies with toggles, future-ready vote interface.
-   **Categories & Heroes**: dynamic hero sections across pages showing live stats (e.g., top score, busiest track).
-   **Auth Experience**: custom registration, login, profile editor, console email password reset, password visibility toggles.
-   **Seed Data**: optional command generates 15+ articles with cover images, interactions, and demo users.
-   **Dark, Reddit-like UI**: gradient heroes, stat chips, redesigned cards, responsive layout.
-   **ASGI**: served via Djangoâ€™s ASGI (through `main.py`) â€“ works with Uvicorn/Gunicorn+Uvloop.
-   **Static Files**: WhiteNoise integrated; fallback cover images per category (Unsplash links).

Environment Variables
---------------------

`config/settings.py` uses defaults suitable for development. Override via environment variables or `.env`:

-   `DJANGO_SECRET_KEY` â€“ set for production.
-   `DJANGO_DEBUG` â€“ `"false"` to disable debug.
-   `DJANGO_ALLOWED_HOSTS` â€“ comma-separated hosts.
-   `EMAIL_BACKEND`, `EMAIL_HOST`, etc. â€“ configure SMTP if replacing console backend.
-   `DATABASE_URL` â€“ use `dj-database-url` or similar if adopting Postgres/MySQL.

Deployment Notes
----------------

-   Collect static: `python manage.py collectstatic`.
-   Configure a real email backend for password reset & notifications.
-   Replace SQLite with Postgres for production; adjust `DATABASES`.
-   Use Gunicorn/Uvicorn workers behind Nginx, with HTTPS and proper `ALLOWED_HOSTS`.
-   Set `DEBUG=False`, provide `SECRET_KEY`, configure `CSRF_TRUSTED_ORIGINS`.

Development Scripts
-------------------

-   **Lint/format**: add `ruff`, `black`, `pre-commit` (not bundled yet).
-   **Tests**: run Django test suite `python manage.py test`. Add coverage as desired.
-   **Demo data**: `python manage.py seed_demo_content --flush-existing`.

Contributing
------------

1.  Fork and clone the repo.
2.  Create a feature branch (`git checkout -b feature/awesome`).
3.  Install dependencies & set up environment (see above).
4.  Run tests (and add new ones).
5.  Submit a pull request describing changes/screenshots.



