# PRC Website — Deployment Guide (Nest Nepal cPanel, MySQL)

Local dev stays on SQLite (`python manage.py runserver` — no env vars needed).
Production uses **MySQL** via environment variables. Nothing is hardcoded.

## 1. Build the package

```bash
python package_deploy.py
```

→ `dist/prc_deploy_<timestamp>.zip` (~28 MB: code + `prc_data.json` data dump +
media files referenced by the DB). Upload this via cPanel File Manager and
extract into the Application Root (e.g. `~/prcapp`).

## 2. Create the MySQL database

cPanel → **MySQL Database Wizard**:
1. Database name: e.g. `prc` (cPanel prefixes it: `<user>_prc`)
2. User + password (SAVE the password)
3. **Collation: `utf8mb4_unicode_ci`** — critical for Nepali (Devanagari) text;
   a latin1 database would store `?????` instead of नेपाली.

## 3. Register the Python app

cPanel → **Setup Python App**:
- Python: 3.12 (or newest available)
- Application root: `prcapp`
- Application URL: your domain
- Startup file: `app.py`

Then click **Run pip install** (uses `requirements.txt` in the app root).

## 4. Connect the project to the database

Pick **one** of these two ways — they achieve the same thing.

### Option A — edit `config/settings.py` (simplest)

At the top of `config/settings.py` there is a clearly marked block:

```python
DB_NAME = ""            # <-- e.g. "sohan_prc"
DB_USER = ""            # <-- e.g. "sohan_prc"
DB_PASSWORD = ""        # <-- the password from the wizard
DB_HOST = "localhost"
DB_PORT = "3306"
```

Paste in the values cPanel shows (the **full** names, including the account
prefix) and re-upload `config/settings.py`. Two trade-offs: this also points
your **local** `runserver` at MySQL, and any later deploy that ships
`settings.py` overwrites what you typed.

### Option B — cPanel environment variables

Setup Python App → your app → **Environment variables** → ADD VARIABLE.
These win over Option A if both are set, so you can keep SQLite locally while
running MySQL on the server.

| Variable | Value |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | long random string (see below) |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `DJANGO_DB` | `mysql` |
| `DJANGO_DB_NAME` | `<cpaneluser>_prc` |
| `DJANGO_DB_USER` | `<cpaneluser>_prc` |
| `DJANGO_DB_PASSWORD` | password from step 2 |
| `DJANGO_SSL_REDIRECT` | `True` *(add only AFTER AutoSSL is working)* |

Only `DJANGO_DB_NAME` + `DJANGO_DB_USER` are actually required for the database
to be used — naming either one switches the project to MySQL. `DJANGO_DB=mysql`
just forces it explicitly.

If neither option is configured on the server, the app deliberately **fails
with a clear error** instead of silently serving an empty SQLite database.
(Set `DJANGO_DB=sqlite` to use SQLite in production on purpose.)

Generate the secret key locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 5. One-time server commands (cPanel Terminal)

```bash
source /home/<user>/virtualenv/prcapp/3.12/bin/activate
cd ~/prcapp

python manage.py migrate                 # creates all tables in MySQL
python manage.py loaddata prc_data.json  # imports ALL site content (fellows, events, ...)
python manage.py createsuperuser         # your admin login
python manage.py collectstatic --noinput
```

Then **Restart** the app in Setup Python App.

## 6. SSL

cPanel → **SSL/TLS Status** → Run AutoSSL. Once `https://` works, ensure the
`DJANGO_SSL_REDIRECT=True` env var is set and Restart again.

## Verifying & updating

- All pages load over https, images render (media + static both served fine).
- `/admin/` → edit content freely; admin edits never need an app restart.
- After template/code changes: re-upload changed files (or a new zip), run
  `collectstatic` if static changed, and **Restart** the app (Passenger caches).

## Notes

- `PyMySQL` (pure Python) is used as the MySQL driver — no compiler needed on cPanel.
- `prc_data.json` is a `dumpdata` export (utf8mb4-safe JSON) generated locally.
  Re-generate it after big content changes if you want the latest content in
  the next deploy: `PYTHONUTF8=1 python manage.py dumpdata --natural-foreign
  --natural-primary --exclude contenttypes --exclude auth --exclude sessions
  --exclude admin --indent 1 -o prc_data.json`
  (`sessions` and `admin` are excluded: session rows are ephemeral, and
  `admin.logentry` references admin users that are not shipped, which would
  break `loaddata` on a fresh server.)
- To redeploy content from scratch on the server:
  `python manage.py flush` → `migrate` → `loaddata prc_data.json`.
- Backups: cPanel daily backups (Standard plan+) + occasional manual download of
  the MySQL dump (cPanel → phpMyAdmin → Export).
