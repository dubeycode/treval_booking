Travel Booking Django App

A web-based travel booking application built with Django 4.2 and MySQL. The project allows users to view and book travel options, and the admin can manage bookings via the Django admin panel.

Features

User registration & login

Travel options listing

Booking system

Admin panel to manage bookings and travel options

Prerequisites

Python 3.10

MySQL (via XAMPP or any MySQL server)

phpMyAdmin (optional for DB management)

Git (for cloning repo)

Local Setup Instructions
1. Clone the Repository
git clone https://github.com/your-username/travel_booking.git
cd travel_booking

2. Setup Virtual Environment (Optional)

If project is on C: drive, you can skip creating a virtual environment.

Otherwise, create one:

python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\Scripts\activate     # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Configure Database

Open phpMyAdmin (http://localhost:8090
).

Create a database named:

travel_booking


Update settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'travel_booking',
        'USER': 'root',        # your MySQL username
        'PASSWORD': '',        # your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

5. Apply Migrations
python manage.py makemigrations
python manage.py migrate

6. Create Superuser
python manage.py createsuperuser


Follow prompts to create admin credentials.

7. Run the Server
python manage.py runserver 8080


Visit the website at: http://127.0.0.1:8080

Admin panel: http://127.0.0.1:8080/admin

Notes

Ensure MySQL service is running in XAMPP before running Django server.

If using PythonAnywhere for hosting, you need to configure a remote MySQL database and update settings.py accordingly.
