# Scoutvision

**Football Scouting and Player Analysis Platform**

Scoutvision is a Django-based football scouting application designed to help scouting teams discover, evaluate, compare, and manage football players.

The application combines player information, statistics, scouting shortlists, recommendations, and role-based evaluation workflows.

> **Project status:** Completed local development project. It has not been presented as a publicly deployed production service.

## Features

### Player database
- Browse and search football players.
- Filter players by position and league.
- View player profiles and available information.

### Player comparison
- Compare up to four players.
- Review player attributes and available statistics.

### Scouting shortlists
- Create and manage player shortlists.
- Add scouting notes and evaluations.
- Export shortlist information to CSV.

### Evaluation workflow
- **Scout:** Discover players and manage shortlists.
- **Analyst:** Review shortlisted players and submit evaluations.
- **Head Scout:** Approve or reject recommendations.
- **Manager:** Access management functionality.

### Administration
- Manage user accounts and profiles.
- Enable or disable ordinary user accounts.
- Review application activity logs.
- Apply role-based access restrictions.

## Technology stack

| Component | Technology |
|---|---|
| Backend | Python, Django |
| Database | MySQL |
| Frontend | HTML, CSS, JavaScript |
| Authentication | Django Authentication |
| Database driver | mysqlclient |
| Environment configuration | python-dotenv |
| Version control | Git, GitHub |

## Project structure

```text
Scoutvision/
|-- core/
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|-- scout/
|   |-- migrations/
|   |-- templates/
|   |-- admin.py
|   |-- api_service.py
|   |-- models.py
|   |-- signals.py
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- .env.example
|-- .gitignore
|-- manage.py
|-- requirements.txt
`-- README.md
```

## Getting started

### 1. Prerequisites

Install:

- Python 3.12 or later.
- MySQL Server.
- Git.

### 2. Clone the repository

```bash
git clone https://github.com/nacirizakaria/Scoutvision.git
cd Scoutvision
```

### 3. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, activate the environment using Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure the following variables:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Development debug setting |
| `ALLOWED_HOSTS` | Allowed host names |
| `DB_NAME` | MySQL database name |
| `DB_USER` | MySQL username |
| `DB_PASSWORD` | MySQL password |
| `DB_HOST` | MySQL server address |
| `DB_PORT` | MySQL server port |

Generate a unique secret key for your environment. Never commit `.env` or publish real credentials.

### 6. Create the MySQL database

For example:

```sql
CREATE DATABASE scouting_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Make sure the database credentials in `.env` match your MySQL configuration.

### 7. Apply migrations

```bash
python manage.py migrate
```

### 8. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the terminal instructions.

### 9. Run the application

```bash
python manage.py runserver
```

Open:

http://127.0.0.1:8000/

The Django development server is intended for local development, not production hosting.

## Running tests

Run the project's automated tests with:

```bash
python manage.py test
```

Check Django configuration with:

```bash
python manage.py check
```

## Security

- Keep secrets in the local `.env` file.
- Do not commit passwords, API keys, or private credentials.
- Use Django's password hashing and authentication mechanisms.
- Preserve CSRF protection for state-changing requests.
- Do not use Django's development server as a production server.

## Project documentation

Additional role and access-control documentation is available in `scout/RBAC.md`.
