# Library Catalog Management System

A Django-based library catalog management system for a school assignment implementing patron and librarian workflows.

## Overview

This system provides:
- **Patron functionality**: Browse catalog, check out items, place holds, request new media
- **Librarian functionality**: Manage catalog, process checkouts/checkins, handle media requests
- **Automatic fine calculation**: $0.25/day for books, $1.00/day for DVDs/CDs

## Technology Stack

- **Backend**: Django 4.x with PostgreSQL
- **Frontend**: HTML templates with Tailwind CSS (CDN), Feather Icons
- **Authentication**: Custom session-based (Patron: card + PIN, Librarian: username + password)

## Project Structure

```
/
├── catalog/                    # Main Django app
│   ├── models.py              # Data models (Patron, Librarian, MediaItem, etc.)
│   ├── views.py               # All view functions
│   └── management/commands/   # Custom commands (populate_data)
├── library_catalog/           # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py                # URL routing
│   └── wsgi.py                # WSGI entry
├── templates/                 # HTML templates
│   ├── main/                  # Public pages (index, login, signup)
│   ├── patron/                # Patron dashboard pages
│   └── librarian/             # Librarian dashboard pages
└── static/                    # Static files
```

## Test Credentials

### Patron Login
- Card Number: `LC-100001`, PIN: `1234` (Sarah Johnson)
- Card Number: `LC-100002`, PIN: `1234` (Michael Chen)

### Librarian Login
- Username: `admin`, Password: `admin123`

## Key Features

### Patron Features
- Browse and search media catalog
- View checked out items and due dates
- Renew items (up to 2 times)
- Place and cancel holds
- Submit media requests

### Librarian Features
- Add/remove catalog items
- Process checkouts to patrons
- Process checkins with automatic fine calculation
- Manage patron accounts
- Approve/reject media requests

## Running the Application

```bash
python manage.py runserver 0.0.0.0:5000
```

## Database Commands

```bash
# Run migrations
python manage.py migrate

# Populate sample data
python manage.py populate_data
```

## Fine Policy

| Media Type | Loan Period | Fine per Day |
|------------|-------------|--------------|
| Books      | 21 days     | $0.45        |
| Audiobooks | 21 days     | $0.45        |
| DVDs       | 7 days      | $0.45        |
| CDs        | 7 days      | $0.45        |
| Magazines  | 14 days     | $0.45        |

## Recent Changes

- December 2024: Initial implementation with all core features
