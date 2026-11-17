# Scoutvision Project Summary

## Overview

Scoutvision is a Django-based football scouting platform. It provides player discovery, comparison, scouting shortlists, player notes, recommendations, role-based workflows, user administration, and activity logging.

The repository describes a local development project. It does not represent a deployed public service or a production hosting environment.

## Main Features

- Browse and search a locally generated football player dataset.
- Filter players by position and league.
- View player profiles and statistics.
- Compare up to four players.
- Create personal scouting shortlists and export them to CSV.
- Record player notes and ratings.
- Generate player recommendations using application-defined criteria.
- Support Scout, Analyst, Head Scout, and Manager roles.
- Review player recommendations and manage approval workflows.
- Manage users and inspect activity logs.

## Technology

- Python and Django
- MySQL database backend configured through environment variables
- Django authentication and groups
- Django templates, HTML, CSS, and JavaScript
- Local player-data generation in `scout/local_players.py`

The player data service is local and synthetic. The application should not be described as connected to a live football data provider unless such an integration is implemented separately.

## Repository Structure

```text
Scoutvision/
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── scout/
│   ├── migrations/
│   ├── templates/scout/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── api_service.py
│   ├── local_players.py
│   ├── signals.py
│   ├── admin.py
│   ├── tests.py
│   └── RBAC.md
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── PROJECT_SUMMARY.md
```

## Data Models

The current application models include:

- `Shortlist`: a user's saved player entries, including player details and notes.
- `PlayerNote`: scouting notes and ratings associated with a user and player.
- `Profile`: user role, assigned scout, biography, and phone field.
- `PlayerApproval`: analyst recommendations and Head Scout decisions.
- `ActivityLog`: user actions, optional IP address, and timestamp.

Django's built-in User model handles authentication. Passwords must be managed through Django's password-hashing mechanisms, not stored as plaintext profile fields.

## Roles and Workflow

The application defines four profile roles:

- **Scout**: discovers players and manages scouting shortlists.
- **Analyst**: reviews assigned scouting entries and submits evaluations.
- **Head Scout**: reviews recommendations and records approval decisions.
- **Manager**: manages users and administrative workflows.

Access is enforced in application views using authentication and role/permission checks. See `scout/RBAC.md` for the documented permission map.

## Configuration and Security

- Local configuration is loaded from a `.env` file.
- `.env.example` contains placeholders only and is safe to copy as a starting point.
- The real `.env` file must never be committed.
- `SECRET_KEY` is required; the settings module does not provide a development fallback.
- `DEBUG` defaults to `False` when not explicitly configured.
- The database connection uses environment variables for database name, user, password, host, and port.
- The repository includes migrations that preserve the database schema's evolution, including removal of the former plaintext profile-password field.

Do not place real credentials, personal data exports, database dumps, or local backup files in the repository.

## Tests

Django test cases are present in `scout/tests.py`. They cover selected authenticated access, the player statistics endpoint, and profile creation through the user signal.

The presence of tests does not by itself establish that they pass. Run the test suite in a configured local environment and record the actual result before relying on it.

## Local Development

Refer to `README.md` for setup instructions. The project requires its Python dependencies and a configured MySQL database. No root `requirements.txt` or `pyproject.toml` is currently included in this repository.

The Django development server is for local development and should not be exposed as a production service.

## Scope and Limitations

- Player records are generated locally and are not a verified live football data feed.
- Recommendation results depend on the application's current rules and available player fields.
- The repository is source code, not a hosted application.
- Production deployment, hosting, and operational security require separate configuration and review.
