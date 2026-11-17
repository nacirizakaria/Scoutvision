
# Scoutvision

**Football Scouting and Player Analysis Platform**

Scoutvision is a Django-based football scouting application designed to help scouting teams discover, evaluate, compare, and manage football players.

The platform brings player information, statistics, scouting shortlists, recommendations, and team evaluation workflows together in one interface.

The project is developed and operated locally.

> **Project status:** Completed local project. The application runs in a local development environment. It is not presented as a publicly deployed or production-hosted service.

---

## Features

### 1. Player Database
- Browse football players by position.
- Search players by name.
- Filter players by position and league.
- View player information, including age, nationality, height, preferred foot, team, and market value.
- Sort player listings using available criteria.
- Browse player profiles.

### 2. Player Comparison
- Compare multiple players side by side.
- Select up to four players for comparison.
- Review player attributes and available statistics.
- Use comparison results to support scouting decisions.

### 3. Player Statistics
- View detailed player statistics.
- Retrieve player match statistics through the application API.
- Display statistical information through the player interface.

### 4. Scouting Shortlists
- Add players to personal shortlists.
- Remove players from shortlists.
- Review shortlisted players.
- Export shortlist information to CSV.
- Keep scouting notes and player evaluations.

### 5. Player Recommendations
- Access player recommendations through the recommendation interface.
- Use available player information and evaluation criteria to support discovery.

### 6. Scouting Workflow
The platform includes different stages of player evaluation:

- Scout: discover and shortlist players.
- Analyst: review shortlisted players and provide evaluations.
- Head Scout: manage approval workflows.
- Manager: access administrative functionality.

### 7. User Management and Access Control
The application includes role-based permissions for:

| Role | Main responsibilities |
|---|---|
| Scout | Browse players, compare players, create and manage shortlists |
| Analyst | Review players and provide evaluations |
| Head Scout | Manage scouting approvals and workflow |
| Manager | Administrative access and user management |

### 8. Administration and Activity Logs
- Manage application users.
- Enable or disable user accounts.
- Review application activity logs.
- Track user actions through the activity logging system.
- Manage user profiles.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Backend | Python, Django |
| Database | MySQL |
| Frontend | HTML, CSS, JavaScript |
| Data processing | Python |
| Player data | Local player dataset and application data services |
| Statistical interface | JavaScript and chart-based visualizations |
| Authentication | Django Authentication |
| Access control | Django Groups and custom role permissions |
| Version control | Git, GitHub |

---

## Project Structure

```text
Scoutvision/
│
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── scout/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── api_service.py
│   ├── templates/
│   └── ...
│
├── manage.py
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Prerequisites

Make sure the following tools are installed:

- Python version compatible with the project dependencies.
- MySQL Server.
- pip.
- Git.

### 2. Clone the repository

```bash
git clone https://github.com/nacirizakaria/Scoutvision.git
cd Scoutvision
```

### 3. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, use Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### 4. Install dependencies

Install the Python dependencies required by the project.

```bash
python -m pip install --upgrade pip
```

The repository does not currently include a root `requirements.txt`.

Install the dependencies used by the project according to your local development environment.

### 5. Configure environment variables

Create a local `.env` file by copying `.env.example`. The settings module loads this file at startup.

**PowerShell:**

```powershell
Copy-Item .env.example .env
```

Generate a strong Django secret key and replace the `SECRET_KEY` placeholder. Keep `DEBUG=False` unless you specifically need local debugging. Update the database settings for your local MySQL installation.

Never put real passwords, API keys, or other sensitive credentials in `.env.example` or commit your `.env` file to GitHub. The application intentionally fails to start if `SECRET_KEY` is missing.

### 6. Configure MySQL

Create a MySQL database for the application.

Example:

```sql
CREATE DATABASE scoutvision
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Update the database configuration in the application's settings or environment variables to match your local MySQL credentials.

### 7. Apply database migrations

```bash
python manage.py migrate
```

The repository already includes database migrations. Use `makemigrations` only when you intentionally change Django models.

### 8. Create an administrator account

```bash
python manage.py createsuperuser
```

Follow the terminal instructions.

### 9. Start the application

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

The application runs locally using Django's development server.

---

## Testing

The project includes Django tests in:

```text
scout/tests.py
```

Run the tests using:

```bash
python manage.py test
```

For more detailed output:

```bash
python manage.py test --verbosity 2
```

The repository contains test cases for access permissions, statistics endpoints, and profile creation.

**Testing status:** The tests are present in the repository, but their latest execution results have not yet been verified.

---

## Local Development

Scoutvision is intended to run in a local development environment.

The repository should not be interpreted as evidence of:

- A publicly hosted application.
- A production deployment.
- A live external football data service.
- A publicly accessible database.

Player information and application functionality should be understood in the context of the local project configuration.

---

## Future Improvements

Potential areas for further development include:

- Expand automated test coverage.
- Improve player evaluation and recommendation criteria.
- Integrate verified external football data providers.
- Improve player performance analytics.
- Strengthen authentication and password handling.
- Prepare a secure production deployment.

---

## Author

**Zakaria Naciri**

Computer Science & Networks Engineering Student
EMSI Casablanca, Morocco

- GitHub: [@nacirizakaria](https://github.com/nacirizakaria)
- LinkedIn: [Zakaria Naciri](https://www.linkedin.com/in/zakaria-naciri-6825aa375/)
- Instagram: [@znaciri20](https://www.instagram.com/znaciri20/)

---

## License

No license has been specified for this repository.
