# Security Policy

## Project status

Scoutvision is a locally developed Django project. It is not currently
advertised as a production-hosted service.

## Supported versions

Security fixes are currently considered for the latest version on the
default branch.

## Reporting a vulnerability

Please do not publish security vulnerabilities, credentials, or
exploitable details in public issues.

Use GitHub's private vulnerability reporting feature for this repository
if it is enabled. Otherwise, contact the repository maintainer privately
through GitHub.

Include:
- A description of the vulnerability.
- Steps to reproduce it.
- Its potential impact.
- Any suggested mitigation.

Do not include real user passwords, secret keys, or private personal data
in a report.

## Security recommendations

- Keep `.env` out of version control.
- Use a unique Django `SECRET_KEY`.
- Set `DEBUG=False` outside local development.
- Configure `ALLOWED_HOSTS` appropriately.
- Use HTTPS and secure cookie settings when deploying.
- Never expose database credentials or API keys.
- Run Django's deployment checks before production deployment.

The Django development server is not suitable for production hosting.
