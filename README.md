# Bright Abroad China

### Bright Beyond Borders

Student agency management system for a brighter future beyond borders.

This project is a simple Django-based student agency system. It helps manage students who want to study abroad, track their documents, monitor progress, and manage applications step by step.

The system is built for two main users:

- Students
- Agency staff

It is designed to make the whole student application process easier to organize and follow.

---

## About the Project

This application is made for a student agency that helps students with university applications, visa processing, document collection, and progress tracking.

Students can create and update their profile, add academic records, upload required documents, and see their current application status.

Agency staff can manage student records, applications, documents, timelines, and notifications from one place.

---

## Main Features

- User registration and login
- Student and staff role system
- Student profile management
- Academic record adding and tracking
- Document tracking for application requirements
- Progress tracking for each student
- University and course application management
- Offer letter and visa processing status updates
- Agency dashboard for staff
- Notifications for important updates
- Blog publishing with rich-text editing, categories, tags, featured images, and SEO/social previews
- Custom error pages
- PWA support for app-like behavior

---

## Tech Stack

- Python
- Django
- SQLite database
- HTML, CSS, JavaScript
- Django templates

---

## Project Structure

```bash
student_agency/
├── accounts/
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── error_views.py
│   └── wsgi.py
├── students/
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── signals.py
├── templates/
│   ├── accounts/
│   └── students/
├── static/
├── manage.py
├── db.sqlite3
├── requirements.txt
└── README.md
```

---

## Installation

Follow these steps to run the project on your computer.

### 1. Clone the project

```bash
git clone <your-repository-link>
cd student_agency
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

On Windows:

```bash
venv\Scripts\activate
```

On Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

### 6. Run the project

```bash
python manage.py runserver
```

Then open:

```bash
http://127.0.0.1:8000/
```

## Deploying on cPanel (Passenger)

The project is configured for cPanel's **Setup Python App** (Passenger) and the
domain `brightabroadchina.webnestle.com`.

1. In cPanel, create the `brightabroadchina.webnestle.com` subdomain and enable
   AutoSSL. Point its DNS to the hosting account if the domain is managed
   elsewhere.
2. Open **Setup Python App**, create an application using a Python version
   supported by the installed Django release, and set the application root to a
   directory outside `public_html` (for example `brightabroadchina_app`). Map
   the application to the new subdomain. Set the startup file to
   `passenger_wsgi.py` and the entry point to `application`. cPanel normally
   creates the Passenger `.htaccess` file for this application; keep that
   generated file.
3. Upload the project source to the application root. Do not upload the local
   `venv/`, `.git/`, or Python cache directories. Include `passenger_wsgi.py`,
   `requirements.txt`, templates, apps, `static/`, and `config/`. Keep the
   `media/` folder and copy any existing blog cover images into it.
4. Install packages in the Python application's virtual environment:

   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` in the application root. Generate a unique
   key in the cPanel terminal with the application's Python interpreter:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Put that value in `SECRET_KEY`. Keep `.env` private (permissions `600` if
   available); it is excluded from Git. Keep `DEBUG=False`, set
   `ALLOWED_HOSTS=brightabroadchina.webnestle.com`, and set the HTTPS origin in
   `CSRF_TRUSTED_ORIGINS`.
6. Configure a database. For a small initial install, SQLite is enabled by
   default; ensure the application root and database file are writable by the
   cPanel application user. For a live site with multiple workers or more data,
   create a cPanel MySQL database and user, grant the user all privileges on
   that database, then set `DB_ENGINE=mysql`, `DB_NAME`, `DB_USER`,
   `DB_PASSWORD`, `DB_HOST=localhost`, and `DB_PORT=3306` in `.env`. PyMySQL is
   included in `requirements.txt`. Do not replace an existing database without
   backing it up and migrating its data.
7. After AutoSSL is active, enable `SECURE_SSL_REDIRECT=True`,
   `SESSION_COOKIE_SECURE=True`, and `CSRF_COOKIE_SECURE=True` in `.env`.
   Restart the Python application after changing environment settings.
8. Run the deployment commands from the application root using the cPanel
   virtual environment's Python:

   ```bash
   python manage.py check --deploy
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

   `collectstatic` puts assets in `staticfiles/`; WhiteNoise serves them.
   Passenger serves the app, while public blog cover images are served under
   `/media/blog/covers/`. Back up the database and `media/` folder regularly.
9. In **Setup Python App**, press **Restart**, then visit
   `https://brightabroadchina.webnestle.com/` and test registration, login,
   `/admin/`, blog cover images, and static assets.

Do not expose `.env`, the database file, or the application source through
`public_html`. The app root should remain outside the public document root.

## Blog publishing

Agency staff can open **Manage blog** from the workspace menu or visit
`/blog/manage/` to create, edit, and publish articles. The editor supports
headings, links, lists, quotes, and tables; each post can also have a category,
tags, a featured thumbnail, and custom search metadata. Published articles
appear on the homepage and at `/blog/`, with related articles and social-share
previews on each post page.

Superusers can also manage posts, categories, and tags in Django Admin at
`/admin/`. The project serves uploaded thumbnails from `/media/` during
development; configure the production web server or media storage to serve
`MEDIA_ROOT` at `MEDIA_URL`.

---

## How the System Works

### Student side

Students can:

- sign up and log in
- complete their profile
- add personal and academic information
- check document requirements
- update application progress
- see notifications
- track their study application process

### Staff side

Agency staff can:

- manage all student records
- create and update applications
- add missing documents
- track timelines and progress
- update statuses like registration, verification, offer letter, and visa processing
- monitor student journey from start to finish

---

## Important Status Flow

The project follows a student application lifecycle such as:

- Registered
- Documents Collection
- Documents Verification
- University Application
- Offer Letter
- Visa Processing
- Completed

This helps keep the application process clear and organized.

---

## Admin Panel

You can access the Django admin panel here:

```bash
http://127.0.0.1:8000/admin/
```

Use the superuser account created earlier to log in.

---

## Notes

- This project is a good base for a student consulting or education agency system.
- It can be expanded with features like document upload, payment tracking, email notifications, and SMS alerts.
- The app uses SQLite by default, which is suitable for development and testing.

---

## License

This project is for educational and personal use unless otherwise specified by the owner.

---

## Developer Note

This is a clean and practical Django project for managing student applications and agency operations. It is simple, easy to understand, and suitable for learning, improvement, and further customization.
