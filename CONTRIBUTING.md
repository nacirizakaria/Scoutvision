# Contributing to Scoutvision

Thank you for your interest in contributing.

## Before making changes

1. Fork the repository or create a feature branch.
2. Create and activate a Python virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Configure your local `.env` file using `.env.example`.
5. Configure a local MySQL database.

## Development guidelines

- Keep changes focused and easy to review.
- Follow existing Django and Python conventions.
- Do not commit `.env`, credentials, database files, or local backups.
- Do not store plaintext passwords.
- Preserve authentication, authorization, and CSRF protections.
- Add or update automated tests when changing application behavior.
- Do not commit generated files or virtual environments.

## Testing

Before submitting a change, run:

```bash
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run
git diff --check
```

## Pull requests

1. Use a descriptive branch name.
2. Explain the purpose of the change.
3. Describe relevant security or database implications.
4. Include test results.
5. Keep pull requests focused on one topic.

Please do not include secrets, personal data, or production credentials
in issues or pull requests.
