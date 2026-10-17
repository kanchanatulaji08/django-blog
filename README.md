# Django Blog

A beginner-friendly blog built with Django. It covers the core things every Django
interview asks about: models, class-based views, templates, forms, authentication,
the admin panel, search, pagination, and tests.

## Features

- User registration, login and logout (email required, duplicate emails rejected)
- Create, edit and delete your own posts (only the author can edit or delete)
- Draft and Published status (drafts are visible only to their author)
- Categories with post counts in the sidebar
- Comments (login required; removable by the comment's author or the post's author)
- Search (`?q=`) and pagination
- "My posts" page that includes drafts
- Django admin for posts, categories and comments
- Automated tests (`blog/tests.py`)

## Setup

Requires Python 3.10+.

```bash
cd django_blog

# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database tables
python manage.py makemigrations blog
python manage.py migrate

# 4. Create an admin user
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for the admin.

**First steps after starting:** log in to the admin, add a few categories, then sign up as a
normal user on the site and write your first post.

## Run the tests

```bash
python manage.py test
```

## Project structure

```
django_blog/
├── manage.py
├── requirements.txt
├── config/                 # project settings, root URLs
├── blog/                   # posts, categories, comments
│   ├── models.py           # Category, Post, Comment
│   ├── views.py            # list, detail, create/update/delete, comments
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── context_processors.py   # sidebar categories
│   └── tests.py
├── accounts/               # registration, login, logout
├── templates/              # base.html, blog/*, accounts/*
└── static/css/style.css
```

## URLs

| URL | Page |
| --- | --- |
| `/` | Latest posts (supports `?q=search&page=2`) |
| `/category/<slug>/` | Posts in a category |
| `/post/<slug>/` | Post detail and comments |
| `/new/` | Write a post (login required) |
| `/post/<slug>/edit/` | Edit post (author only) |
| `/post/<slug>/delete/` | Delete post (author only) |
| `/my-posts/` | Your posts, including drafts |
| `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` | Authentication |
| `/admin/` | Admin panel |

## Configuration (environment variables)

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | insecure dev key | **Set a real secret in production** |
| `DJANGO_DEBUG` | `True` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hostnames |

## Deploying (Render, Railway, PythonAnywhere)

1. Push the project to GitHub.
2. Set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS` on the host.
3. For static files on Render/Railway, add `whitenoise` and `gunicorn` to `requirements.txt`,
   add `whitenoise.middleware.WhiteNoiseMiddleware` right after `SecurityMiddleware`, and run
   `python manage.py collectstatic --noinput` during the build.
4. For a real database, switch `DATABASES` in `config/settings.py` to PostgreSQL
   (e.g. with `dj-database-url` and a `DATABASE_URL` variable).
5. Start command: `gunicorn config.wsgi`.

## Ideas to extend it

- Rich-text editor or Markdown support for post bodies
- Post images (`ImageField` + `MEDIA_ROOT`)
- Tags, likes, user profile pages
- A REST API with Django REST Framework and JWT authentication (a great second project)
