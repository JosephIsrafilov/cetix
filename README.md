Cetix

Habr-inspired Django platform for publishing curated engineering articles with moderation workflow, role-based permissions, comments, reactions, bookmarks, and a sleek dark theme.

Site Overall
-----------
- Home feed with spotlight hero and stat chips
- Article detail with reactions/bookmarks and threaded comments
- Category and author hubs with gradient cards

Requirements
------------

-   Python 3.12
-   pip / virtualenv
-   SQLite (bundled) -- or configure your own database via `DATABASES`

Quick Start
-----------
1. **Clone the repository**

       git clone https://github.com/JosephIsrafilov/cetix.git
       cd cetix

2. **Create and activate a virtual environment**

       python -m venv .venv
       # Windows PowerShell
       .\.venv\Scripts\Activate.ps1
       # macOS/Linux
       source .venv/bin/activate

3. **Install dependencies**

       pip install --upgrade pip
       pip install -r requirements.txt

4. **Apply migrations and seed demo data**

       python manage.py migrate
       python manage.py seed_demo_content --flush-existing  # optional sample data
        python manage.py migrate
        python manage.py seed_demo_content --flush-existing  #sample data for project


5. **Create a superuser (optional but useful)**
       python manage.py createsuperuser

6. **Run the development server**

       python manage.py runserver
       # or ASGI/FastAPI-style entry via Uvicorn:
       python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

7. **Open the site**

       http://127.0.0.1:8000/

Project Structure
-----------------
-   `accounts/` “ custom user model, roles, profiles, auth forms, password reset.
-   `articles/`
    -   `models.py` “ Category, Article, reactions, bookmarks, comments.
    -   `views.py` “ Feed, detail, category/author listings, moderation, bookmarks.
    -   `forms.py` “ Article creation with moderation awareness, comment form.
    -   `management/commands/seed_demo_content.py` “ Demo seed script (covers, comments, reactions, bookmarks).
-   `templates/` “ Dark themed UI with shared `page_hero` include and React-style interactions using vanilla JS.
-   `static/css/style.css` “ Reddit-inspired styling, gradients, hero themes.
-   `static/js/`
    -   `password-toggle.js` “ toggles password visibility.
    -   `reactions.js` “ optimistic like/dislike updates with fetch + session storage.
    -   `comments.js` / `layout.js` “ comment interactions, profile dropdown.
-   `main.py` “ ASGI entrypoint for Uvicorn.
-   `config/` “ Project settings/urls.
-   `requirements.txt` “ Django, Pillow, Requests, Uvicorn (standard), WhiteNoise.

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
-   **ASGI**: served via Django™s ASGI (through `main.py`) “ works with Uvicorn/Gunicorn+Uvloop.
-   **Static Files**: WhiteNoise integrated; fallback cover images per category (Unsplash links).

Environment Variables
---------------------

`config/settings.py` uses defaults suitable for development. Override via environment variables or `.env`:

-   `DJANGO_SECRET_KEY` “ set for production.
-   `DJANGO_DEBUG` “ `"false"` to disable debug.
-   `DJANGO_ALLOWED_HOSTS` “ comma-separated hosts.
-   `EMAIL_BACKEND`, `EMAIL_HOST`, etc. “ configure SMTP if replacing console backend.
-   `DATABASE_URL` “ use `dj-database-url` or similar if adopting Postgres/MySQL.
=======
- `accounts/` -- custom user model, roles, profiles, auth forms, password reset.
- `articles/`
  - `models.py` -- Category, Article, reactions, bookmarks, comments.
  - `views.py` -- Feed, detail, category/author listings, moderation, bookmarks.
  - `forms.py` -- Article creation with moderation awareness, comment form.
  - `management/commands/seed_demo_content.py` -- Demo seed script (covers, comments, reactions, bookmarks).
- `templates/` -- Dark themed UI with shared `page_hero` include and vanilla JS interactions.
- `static/css/style.css` -- Reddit-inspired styling, gradients, hero themes.
- `static/js/` -- password toggles, reaction fetch handler, comment helpers.
- `main.py` -- ASGI entrypoint for Uvicorn.
- `config/` -- project settings/urls.
- `requirements.txt` -- Django, Pillow, Requests, Uvicorn, WhiteNoise.

Feature Overview
----------------
- **Roles**: guest, user, admin, super admin.
- **Moderation**: user submissions require admin approval; moderation queue for publish/reject.
- **Bookmarks & Reactions**: optimistic like/dislike toggle, personal reading list.
- **Comments**: threaded replies, future-ready vote buttons.
- **Dynamic heroes**: stat-driven hero sections across latest, popular, categories, bookmarks, moderation.
- **Auth experience**: custom registration, profile editor, console email password reset, password visibility toggle.
- **Seed data**: optional command generates demo users, articles, reactions, comments.
- **UI**: dark, Reddit-like aesthetic; gradient cards, stat chips, responsive layout.
- **ASGI-ready**: run via `python manage.py runserver` or `uvicorn main:app`.
- **Static files**: WhiteNoise integrated; category-level fallback cover art.

Environment Variables
---------------------
Customize via env vars or `.env`:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`false` for production)
- `DJANGO_ALLOWED_HOSTS`
- Email settings (`EMAIL_BACKEND`, `EMAIL_HOST`, etc.)
- `DATABASE_URL` if using Postgres/MySQL

Deployment Notes
----------------
- Collect static: `python manage.py collectstatic`
- Configure SMTP backend for password reset
- Switch to Postgres for production
- Use Gunicorn/Uvicorn behind Nginx
- Set `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`

Development Scripts
-------------------
- Lint/format: integrate `ruff`, `black`, `pre-commit`
- Tests: `python manage.py test`
- Seed demo data: `python manage.py seed_demo_content --flush-existing`
