# DIY Blog Platform

A modern, feature-rich blogging platform built with Django that allows users to create, manage, and share their blog posts with a beautiful user interface.

## Features

- User Authentication & Authorization
- Blog Post Management (Create, Read, Update, Delete)
- Category-based Post Organization
- Comment System
- User Profiles
- Responsive Design
- Modern UI with Tailwind CSS
- Search Functionality
- Pagination
- Admin Dashboard

## Tech Stack

- Python 3.12.1
- Django 5.0.2
- Tailwind CSS
- PostgreSQL (for production)
- Gunicorn (for production)

## Prerequisites

- Python 3.12.1 or higher
- pip (Python package manager)
- Node.js and npm (for Tailwind CSS)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd diyblog
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tailwind CSS:
```bash
npm install
```

5. Build Tailwind CSS:
```bash
npm run build
```

6. Set up environment variables:
Create a `.env` file in the project root with:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

7. Run migrations:
```bash
python manage.py migrate
```

8. Create a superuser:
```bash
python manage.py createsuperuser
```

9. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
diyblog/
├── blog/                 # Main blog application
│   ├── migrations/      # Database migrations
│   ├── static/         # Static files
│   ├── templates/      # HTML templates
│   ├── admin.py        # Admin configuration
│   ├── apps.py         # App configuration
│   ├── models.py       # Database models
│   ├── urls.py         # URL routing
│   └── views.py        # View logic
├── diyblog/            # Project settings
│   ├── settings.py     # Project settings
│   ├── urls.py         # Main URL routing
│   └── wsgi.py         # WSGI configuration
├── static/             # Project-wide static files
├── templates/          # Project-wide templates
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
├── tailwind.config.js  # Tailwind CSS configuration
└── wsgi.py            # WSGI entry point
```

## Deployment

The project is configured for deployment on platforms like Render or Heroku.

1. Create a new web service on your deployment platform
2. Connect your repository
3. Set the following environment variables:
   - `DEBUG=False`
   - `SECRET_KEY=<your-secret-key>`
   - `DATABASE_URL=<your-database-url>`
4. Set the build command:
   ```bash
   pip install -r requirements.txt && npm install && npm run build
   ```
5. Set the start command:
   ```bash
   gunicorn wsgi:application
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Documentation
- Tailwind CSS
- All contributors and users of the platform 