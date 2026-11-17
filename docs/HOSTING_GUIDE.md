# Hosting the PRC Website on cPanel — Complete Guide

## Project overview

- **Framework:** Django 6.1 (Python 3.12)
- **Database:** MySQL on production (SQLite for local dev)
- **Static files:** WhiteNoise (served by Django, no separate web server needed)
- **Media files:** uploaded images served by Django at `/media/`
- **Deployment package:** built with `python package_deploy.py` → `dist/prc_deploy_*.zip`
- **Content dump:** `prc_data.json` (all site content as JSON for fresh-server import)
- **Entry points:** `app.py` (recommended startup file) and `passenger_wsgi.py` (fallback, both work)

---

## Phase 1 — Build the deploy package

Run this **on your local machine** (where `manage.py` lives):

```bash
python package_deploy.py
```

This creates `dist/prc_deploy_YYYYMMDD_HHMM.zip` containing only what the server needs:

- `manage.py`, `app.py`, `requirements.txt`, `prc_data.json`
- `config/` (settings, URLs, wsgi, migrations)
- `website/` (app code, templates, models, migrations — minus `tests.py` and `management/`)
- `media/` (only DB-referenced images by default; use `--all-media` to include everything)

**Size:** ~28 MB typically. The `staticfiles/` folder is deliberately excluded — the server regenerates it with `collectstatic`.

> **Pro tip:** If you have changed any content since the last `prc_data.json` dump, regenerate it first:
> ```bash
> PYTHONUTF8=1 python manage.py dumpdata --natural-foreign --natural-primary \
>   --exclude contenttypes --exclude auth --exclude sessions --exclude admin \
>   --indent 1 -o prc_data.json
> ```

---

## Phase 2 — Upload to cPanel

1. Open **cPanel → File Manager**
2. Navigate to your home directory (e.g. `/home/sohan`)
3. Create the app folder, e.g. `prcapp`
4. Upload the zip into that folder
5. **Extract** the zip inside `prcapp` (right-click → Extract)
6. Verify: `prcapp/manage.py` should exist, `prcapp/config/settings.py` should exist

Your folder structure should look like:

```
/home/sohan/prcapp/
├── app.py
├── manage.py
├── requirements.txt
├── prc_data.json
├── passenger_wsgi.py          ← created for you (fallback entry point)
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── migrations/
├── website/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── website/
│   │       ├── home.html
│   │       ├── constitution.html
│   │       ├── events.html
│   │       └── ... (all page templates)
│   └── migrations/
└── media/
    ├── constitution/
    ├── events/
    └── ... (DB-referenced images)
```

---

## Phase 3 — Create the MySQL database

Go to **cPanel → MySQL Database Wizard**:

1. **Create a database:** name it `prc` (or whatever you like). cPanel will prefix it with your account name, e.g. `sohan_prc`.

2. **Create a user:** choose a username and a **strong password**. Save the password somewhere safe.

3. **Add user to database:** grant **ALL PRIVILEGES**.

4. **COLLATION IS CRITICAL:** when creating the database, make sure the collation is **`utf8mb4_unicode_ci`**. If it's `latin1` or `utf8mb4_general_ci`, Nepali (Devanagari) text will be stored and displayed as `?????` instead of नेपाली.

   - In the MySQL Database Wizard, the collation option may appear during database creation
   - If you've already created it, check in **phpMyAdmin**: click the database → Operations tab → look at "Collation"
   - If wrong, you may need to recreate the database with the correct collation. There's no easy in-place conversion.

---

## Phase 4 — Register the Python app

Go to **cPanel → Setup Python App**:

1. Click **Create Application**
2. Fill in:
   - **Python version:** 3.12 (or the newest available)
   - **Application root:** `prcapp` (the folder you created)
   - **Application URL:** your domain (e.g. `yourdomain.com` or a subdomain)
   - **Application startup file:** `app.py`
3. Click **Create**

cPanel will now:

- Create a Python virtual environment (e.g. `/home/sohan/virtualenv/prcapp/3.12/`)
- Show you the app's configuration page

**Then:**

4. Click **Run pip install** — this installs from `requirements.txt` in the app root:
   - Django
   - whitenoise
   - Pillow
   - PyMySQL

5. If pip install fails, check the error. Common issues:
   - `requirements.txt` not found → verify it's at `~/prcapp/requirements.txt`
   - PyMySQL install issues → it's pure Python, should not need a compiler

---

## Phase 5 — Connect to the database

You have **two options**. Pick one.

### Option A — Edit `config/settings.py` (simplest, but affects local dev too)

1. Open `config/settings.py` in cPanel File Manager (or edit locally and re-upload)
2. At the top, fill in the DATABASE SETUP block:

   ```python
   DB_NAME = "sohan_prc"          # full cPanel name (account prefix + your name)
   DB_USER = "sohan_prc"          # same — the user you created
   DB_PASSWORD = "your_password"  # the password from step 3
   DB_HOST = "localhost"          # keep as-is
   DB_PORT = "3306"               # keep as-is
   ```

3. Re-upload the edited `settings.py`

**Trade-off:** this also switches your local `runserver` to MySQL. Any future deploy that uploads `settings.py` overwrites your changes.

### Option B — cPanel environment variables (recommended)

Leave `config/settings.py` untouched. Set these in **Setup Python App → your app → Environment variables → ADD VARIABLE**:

| Variable | Value |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | a long random string |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `DJANGO_DB` | `mysql` |
| `DJANGO_DB_NAME` | `sohan_prc` |
| `DJANGO_DB_USER` | `sohan_prc` |
| `DJANGO_DB_PASSWORD` | `your_password` |

Generate a secret key locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Why this is better:** you keep SQLite locally, and the env vars override the empty `DB_NAME`/`DB_USER` in settings.py on the server.

> **Note:** `DJANGO_DB_NAME` + `DJANGO_DB_USER` are the minimum needed to switch to MySQL. `DJANGO_DB=mysql` just makes it explicit. If neither option is configured, the app deliberately fails with a clear error (it won't silently serve an empty SQLite database).

---

## Phase 6 — One-time server setup (cPanel Terminal)

Go to **cPanel → Terminal** (or SSH if you have it). Then run:

```bash
# Activate the app's virtual environment
source /home/sohan/virtualenv/prcapp/3.12/bin/activate
cd ~/prcapp

# 1. Create all database tables
python manage.py migrate

# 2. Import all site content from the JSON dump
python manage.py loaddata prc_data.json

# 3. Create your admin login
python manage.py createsuperuser

# 4. Collect static files for WhiteNoise
python manage.py collectstatic --noinput
```

> **If `loaddata` complains about missing contenttypes or auth entries:** this is expected — the dump excludes those apps intentionally (they're created by `migrate` and are site-specific). The dump only contains your actual content models.

> **If you get a "no fixture found" error for `prc_data.json`:** verify the file is at `~/prcapp/prc_data.json` (use `ls ~/prcapp/`).

---

## Phase 7 — Restart and verify

1. Go back to **Setup Python App**
2. Click **Restart** next to your app
3. Visit your domain in a browser

**What to check:**

- The homepage loads with all the content (fellows, events, publications, etc.)
- Images render correctly (both static and media)
- Nepali text displays correctly (नेपाली) — if you see `???`, the database collation is wrong
- `/admin/` loads and you can log in with the superuser you created
- No Python errors in the browser (a stack trace means something is wrong)

---

## Phase 8 — Enable HTTPS (SSL)

1. Go to **cPanel → SSL/TLS Status**
2. Click **Run AutoSSL** (or enable auto-renewal)
3. Wait for the certificate to be issued (usually a few minutes)
4. Once `https://yourdomain.com` works:
   - Add environment variable `DJANGO_SSL_REDIRECT=True` in Setup Python App
   - **Restart** the app again

After this, all HTTP requests redirect to HTTPS. The existing `SECURE_PROXY_SSL_HEADER` setting handles the cPanel proxy forwarding the `X-Forwarded-Proto: https` header correctly.

---

## Phase 9 — Updating the site later

### After content changes in the admin

No restart needed. Admin edits to pages, events, fellows, etc. are live immediately.

### After code/template changes

1. Make your changes locally
2. Rebuild the package: `python package_deploy.py`
3. Upload the new zip, extract over the existing files (or just upload changed files individually)
4. If static files changed: run `python manage.py collectstatic --noinput` in cPanel Terminal
5. **Restart** the app in Setup Python App (Passenger caches Python modules — a restart is required)

### After adding new content models or fields

1. Make migrations locally: `python manage.py makemigrations`
2. Include the new migration files in the deploy package (they're in `config/` or `website/migrations/`)
3. Upload, then on the server run: `python manage.py migrate`
4. Restart

### Refreshing content from scratch

If you want to wipe and re-import all content (e.g. after a major data update):

```bash
source /home/sohan/virtualenv/prcapp/3.12/bin/activate
cd ~/prcapp
python manage.py flush        # clears all data tables
python manage.py migrate      # re-creates tables
python manage.py loaddata prc_data.json   # re-imports content
python manage.py collectstatic --noinput
# Restart the app
```

---

## Troubleshooting

### The app shows a 500 error or a stack trace

- Check that all environment variables are set (especially `DJANGO_DB_NAME` and `DJANGO_DB_USER`)
- Check that the database and user exist and the user has all privileges
- Check that the database collation is `utf8mb4_unicode_ci`
- Look at the app's **Logs** in Setup Python App for the actual error

### Images don't show up

- Verify `collectstatic` ran successfully
- Verify media files are present in `~/prcapp/media/`
- Check that `MEDIA_URL = '/media/'` and `MEDIA_ROOT` is set correctly in settings.py
- The app serves media at `/media/<path>` via `config/urls.py` — no separate media configuration needed

### Nepali text is garbled

- The database collation is wrong. Recreate the database with `utf8mb4_unicode_ci`
- Re-run `loaddata prc_data.json` after fixing the collation

### "Module not found" errors

- Verify `app.py` is set as the startup file in Setup Python App
- Verify the application root is `prcapp` (not a subfolder)
- Check that `passenger_wsgi.py` exists at the app root (now created)
- The virtual environment must be the one cPanel created for this app

### App won't restart or pip install fails

- Check that `requirements.txt` is at the app root (`~/prcapp/requirements.txt`)
- PyMySQL is pure Python — should not need build tools. If it fails, the issue is elsewhere
- Try running pip install manually in Terminal: `source ~/virtualenv/prcapp/3.12/bin/activate && pip install -r ~/prcapp/requirements.txt`

---

## What's already in place

These files are ready for cPanel deployment — no changes needed:

| File | Purpose |
|---|---|
| `app.py` | Startup file for cPanel Setup Python App |
| `passenger_wsgi.py` | Fallback WSGI entry point (created for this deployment) |
| `config/wsgi.py` | Django WSGI configuration |
| `config/settings.py` | Production-ready settings with env var support |
| `config/urls.py` | URL routing including media serving |
| `requirements.txt` | Python dependencies |
| `prc_data.json` | Content dump for fresh-server import |
| `package_deploy.py` | Builds the deploy zip |

### Environment variables reference (full list)

| Variable | Required? | Default | Notes |
|---|---|---|---|
| `DJANGO_DEBUG` | Recommended | `True` (local) | Set to `False` on production |
| `DJANGO_SECRET_KEY` | Recommended | hardcoded dev key | Use a random string in production |
| `DJANGO_ALLOWED_HOSTS` | Recommended | `127.0.0.1,localhost` | Comma-separated list of your domains |
| `DJANGO_DB` | Optional | — | Set to `mysql` to force MySQL, or `sqlite` to use SQLite in production |
| `DJANGO_DB_NAME` | Required for MySQL | empty (→ SQLite) | Full cPanel name: `accountname_prc` |
| `DJANGO_DB_USER` | Required for MySQL | empty (→ SQLite) | Same as above |
| `DJANGO_DB_PASSWORD` | Required for MySQL | empty | From the MySQL wizard |
| `DJANGO_DB_HOST` | Optional | `localhost` | Keep as-is on cPanel |
| `DJANGO_DB_PORT` | Optional | `3306` | Keep as-is on cPanel |
| `DJANGO_SSL_REDIRECT` | Optional | `False` | Set to `True` after AutoSSL is working |
