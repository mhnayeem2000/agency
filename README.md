# Student Agency Management System

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
