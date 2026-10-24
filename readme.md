# OpenWeather

A small, beginner-friendly weather dashboard built with **Django** and the free
[OpenWeather Current Weather API](https://openweathermap.org/current). It was
created as a learning project for consuming a third-party REST API with Python
before moving on to building REST APIs with Django REST Framework.

Search for any city and see its current conditions: temperature, feels-like
temperature, humidity, wind speed, a short description, and the matching
weather icon. The interface is responsive and uses a calm light-blue palette.

## Features

- Search by city name with a simple HTML form (no JavaScript required).
- Current temperature in Celsius, weather description, and icon.
- Optional metrics (feels-like, humidity, wind) shown when the API returns them.
- Friendly messages for missing configuration, invalid keys, unknown cities,
  timeouts, rate limits, and unexpected responses.
- No API key or request URL is ever written into the page or logs.
- Automated tests use mocked HTTP responses, so they need no API key and make
  no network requests.

## Tech stack

- Python 3.13
- Django 5.2
- SQLite (Django's default; no custom models are used by this project)
- `requests` for calling OpenWeather
- `python-dotenv` for loading environment variables from `.env`

## Project structure

```text
openweather/
├── requirements.txt              # canonical dependency list — install this one
├── readme.md
├── .env                          # your secrets (created locally, never committed)
└── projectsite/
    ├── manage.py                 # Django entry point
    ├── db.sqlite3                # local database (generated, never committed)
    ├── requirements.txt          # older, incomplete list retained for reference
    ├── projectsite/
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    └── weather/
        ├── views.py              # API integration and error handling
        ├── tests.py              # mocked tests
        ├── templates/weather.html
        └── static/weather/style.css
```

> **Dependency note:** the root `requirements.txt` is the canonical file. The
> nested `projectsite/requirements.txt` is an older list and is intentionally
> kept but not used. Always install from the repository root.

## Prerequisites

- Python 3.13 (3.10+ should also work with this Django version)
- A free OpenWeather account and API key
- Git

## Setup

Run these commands from the repository root.

### 1. Get the code and enter the project

```powershell
git clone https://github.com/CC6-Pancake/openweather.git
cd openweather
```

### 2. Create and activate a virtual environment

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, either allow local scripts for your
user account once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

or skip activation and call the interpreter directly
(`.\venv\Scripts\python.exe ...`).

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Get a free OpenWeather API key

1. Sign up at <https://home.openweathermap.org/users/sign_up>.
2. Verify your email address.
3. Open the **API keys** tab and copy your default key.
4. New keys can take up to about two hours to activate. Until then, requests
   may be rejected with a 401 error.

### 5. Configure the key in `.env`

Create a file named `.env` in the **repository root** (next to the root
`requirements.txt`) containing one line:

```dotenv
OPENWEATHER_API_KEY=your_key_here
```

Rules:

- Do not wrap the value in quotes or add spaces around `=`.
- Never commit `.env`, paste the key into source code, or share it publicly.
- `.env` is already listed in `.gitignore`; if you fork this project, verify
  that it remains ignored.

The project loads `.env` automatically through `python-dotenv` when Django
starts. A key already exported in your shell also works.

### 6. Apply database migrations

```powershell
cd projectsite
python manage.py migrate
```

This creates `projectsite/db.sqlite3` with Django's built-in tables. The
weather app itself has no models or migrations.

### 7. Start the development server

From `projectsite/`:

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. If the key is missing or invalid, the page will
explain the problem instead of failing silently.

## Running the tests

From `projectsite/`:

```powershell
python manage.py test weather
```

Expected result: all tests pass. The tests mock `requests.get`, so no API key
and no internet connection are required.

Optional sanity check:

```powershell
python manage.py check
```

## Manual verification checklist

With the server running and a valid key configured:

- [ ] <http://127.0.0.1:8000/> shows **Puerto Princesa, PH** by default.
- [ ] Searching **Tokyo** shows Tokyo's current conditions.
- [ ] An unknown city (for example `Nowhereville123`) shows a friendly
      "No weather found" message.
- [ ] An empty search shows "Please enter a city name."
- [ ] The layout stacks into one column on a narrow/mobile viewport.
- [ ] `git status` does not list `.env` or `db.sqlite3`.

Without a key, the page shows a "not configured" message — this is expected and
confirms the configuration check works.

## Configuration and safety notes

- The application never renders the request URL or exception details. Server
  logs record only the city name and HTTP status code.
- `.env`, `venv/`, and `db.sqlite3` are ignored by Git.
- To confirm the ignore rules:

  ```powershell
  git check-ignore -v .env venv/ projectsite/db.sqlite3
  ```

- This project uses Django's development settings (`DEBUG = True`) and a local
  SQLite database. It is intended for learning and local use, not production
  deployment.

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| "The weather service is not configured yet" | `.env` missing, in the wrong place, or key empty | Create `.env` in the repository root and restart the server |
| "rejected the API key" (HTTP 401) | Key is wrong, deactivated, or not yet active | Check the key, wait up to ~2 hours after signup |
| "No weather found" (HTTP 404/400) | City name not recognized | Try `City`, `City,CC` (country code), or a different spelling |
| "Too many requests" (HTTP 429) | Free-tier rate limit reached | Wait a minute and try again |
| Timeout message | No connection or slow network | Check your internet connection |
| `Activate.ps1 cannot be loaded` | PowerShell execution policy | Run the `Set-ExecutionPolicy` command above, or call the venv Python directly |
| `manage.py` not found | Wrong working directory | `cd projectsite` first |

## Notes on scope

This project intentionally stays small: no user accounts, forecasts, geolocation,
search history, caching, or JavaScript frameworks. It exists to practise
consuming a REST API with Django; the next step would be exposing similar data
through a Django REST Framework API.
