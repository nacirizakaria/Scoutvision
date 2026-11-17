# ScoutVision Pro — Project Summary

This file documents the full analysis of the `football_scout` Django project.

## Project Overview

A football scouting platform built with Django. It provides scouts with features to:

- register and login
- browse a local player database
- filter players by position and search by name
- compare players side by side
- view player profiles with advanced stats
- create and manage a personal shortlist
- record scouting notes and ratings
- export shortlist as CSV
- get generated player recommendations

The app uses a local fake data service instead of a real sports API.

---

## Root Files

### `manage.py`
- Standard Django command line utility.
- Sets `DJANGO_SETTINGS_MODULE = core.settings`.

### `.env.example`
- Example environment variables:
  - `SECRET_KEY`
  - `DEBUG`
  - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Intended to configure MySQL, but the repository also contains `db.sqlite3`.

---

## Core Django Project

### `core/settings.py`
- Loads environment variables from `.env` using `dotenv`.
- Configures Django apps and middleware.
- Uses MySQL database settings by default.
- Static files served from `STATIC_URL = 'static/'`.
- Authentication redirects:
  - `LOGIN_URL = '/login/'`
  - `LOGIN_REDIRECT_URL = '/dashboard/'`
  - `LOGOUT_REDIRECT_URL = '/login/'`

### `core/urls.py`
- Routes:
  - `admin/` -> Django admin
  - `` -> includes `scout.urls`

### `core/wsgi.py`
- Standard WSGI entrypoint.

### `core/asgi.py`
- Standard ASGI entrypoint.

---

## Scout App Structure

### `scout/apps.py`
- Defines `ScoutConfig`.

### `scout/admin.py`
- Present but empty.
- No models are registered in admin.

### `scout/tests.py`
- Empty placeholder.

### `scout/models.py`
Defines two models:

- `Shortlist`
  - `scout` (User)
  - `player_id`
  - `player_name`
  - `position`
  - `team`
  - `added_at`
  - `notes`
  - Unique constraint: `(scout, player_id)`

- `PlayerNote`
  - `scout` (User)
  - `player_id`
  - `note`
  - `rating`
  - `created_at`

These models store personal scouting shortlist entries and notes.

### `scout/urls.py`
Routes:

- `/` -> dashboard
- `/login/`, `/register/`, `/logout/`
- `/dashboard/`
- `/players/`
- `/compare/`
- `/player/<pk>/`
- `/player/<pk>/stats/` (AJAX)
- `/recommend/`
- `/shortlist/`
- `/shortlist/add/`
- `/shortlist/remove/`
- `/shortlist/export/`

### `scout/api_service.py`
- Imports everything from `scout/local_players.py`.
- Acts as a facade for the fake local player data service.
- No real external API calls are made.

---

## Data and Business Logic

### `scout/local_players.py`
This file contains the local player data engine:

- Position mapping and labels.
- League, team, and nationality lists.
- A small hard-coded roster of star players.
- Synthetic generation of players from ID 6 to 100.
- Realistic stats generation logic for each position.

#### Helper utilities
- `format_market_value(value)` formats values as `€xM` or `€xK`.
- `enrich_player(player)` adds computed attributes and metadata:
  - `market_value_fmt`
  - `position_label`
  - `attributes` for radar chart
  - `availability`
  - `preferred_foot`
  - `contract_until`
  - `transfers`
  - `strengths` / `weaknesses`
  - `specific_position`
  - `current_team`

#### Data access methods
- `get_leagues()` returns league list.
- `get_players(...)` filters and paginates players.
- `get_player_profile(player_id)` returns a single player by ID.
- `search_players(query, page_size)` searches by player name.
- `get_player_stats(player_id)` generates fake season statistics.
- `format_player_stats(player_data)` makes stats display-friendly.
- `get_player_match_stats(player_id, max_matches)` returns fake recent matches.

This module is the functional core of the app's player database.

---

## Views and Features

### Authentication views
- `login_view(request)` handles login.
- `register_view(request)` handles signup and group assignment.
- `logout_view(request)` logs out the user.

### Dashboard
- `dashboard(request)` builds metrics from local player data:
  - shortlist count
  - recent shortlist
  - total players
  - league count
  - position count
- Renders `scout/dashboard.html`.

### Player browsing
- `players_by_position(request)` supports:
  - filtering by position
  - search by query
  - pagination
- Renders `scout/players.html`.

### Comparison
- `compare_players(request)` loads up to 4 players from GET `ids`.
- Renders `scout/compare.html`.

### Player profile
- `player_profile(request, pk)` displays a detailed profile.
- Supports posting notes and ratings.
- Shows if the player is in the current user's shortlist.

### AJAX stats endpoint
- `player_stats_api(request, pk)` returns JSON containing:
  - `match_stats`
  - `af_stats`
  - `image_url`
- Used by the profile page to render charts.

### Recommendations
- `recommend(request)` filters players and sorts them by score.
- Score factors:
  - availability
  - age fit
  - market value
  - transfer count
- Returns top 12 generated recommendations.

### Shortlist management
- `shortlist(request)` displays saved players.
- `add_to_shortlist(request)` adds a player to the shortlist.
- `remove_shortlist(request)` removes a player.
- `export_shortlist(request)` returns a CSV export.

---

## Templates

### `scout/base.html`
- Global layout with navigation and message display.
- Includes Tailwind CDN and Chart.js.
- Defines UI patterns for cards, buttons, tables, alerts.

### `scout/login.html`
- Login page with a marketing hero panel.
- Styled form and icon-driven layout.

### `scout/register.html`
- Registration page with role selection.
- Signup form and error display.

### `scout/dashboard.html`
- Summary metrics and quick navigation.
- Recent shortlist preview.

### `scout/players.html`
- Player listing page.
- Filters, search, pagination.
- Compare selection stored in `sessionStorage`.
- Player cards support shortlisting and profile navigation.

### `scout/compare.html`
- Side-by-side comparison view.
- Radar and market value charts.
- Transfer history panels.

### `scout/profile.html`
- Detailed player profile.
- AJAX-loaded stats and chart rendering.
- Notes creation and listing.

### `scout/recommend.html`
- Recommendation page with advanced filters.
- Fit score breakdown for each candidate.

### `scout/shortlist.html`
- List of shortlisted players.
- Export CSV button.
- Compare shortcut for top shortlisted players.

---

## Database migrations

### `0001_initial.py`
- Created `PlayerNote`, `TeamFitAnalysis`, and `Shortlist`.
- `TeamFitAnalysis` model later removed.

### `0002_sportapicache_shortlist_sport_id_and_more.py`
- Added `SportAPICache` model.
- Added `sport_id` to `Shortlist`.
- Deleted `TeamFitAnalysis`.

### `0003_delete_sportapicache_remove_shortlist_sport_id.py`
- Deleted `SportAPICache`.
- Removed `sport_id` from `Shortlist`.

This indicates the project was simplified from a more complex earlier design.

---

## Key insights

- The app is a Django MVP for football scouting.
- Player data is locally generated, not fetched from a real API.
- The UI is fully built with Django templates and inline CSS.
- Auth is Django's default user system.
- Shortlists and notes are persistent per user.
- There are no admin registrations or tests defined.

---

## File created
- `PROJECT_SUMMARY.md`

If you want, I can also add a shorter resume-style summary or a detailed architecture diagram file.
