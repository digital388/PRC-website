# Deploying from GitHub to cPanel

The repository is the source of truth. cPanel clones it once, and each update is
`git push` → cPanel **Pull** → **Deploy HEAD Commit** (runs `.cpanel.yml`) →
`migrate` + `collectstatic` → **Restart**.

Assumptions: cPanel user `pokharac`, app root `~/prcapp`, Python 3.12 app named
`prcapp`. Substitute your own values.

---

## 1. Push the repository to GitHub

The local repo is already initialised with one commit on `main`.

1. On GitHub: **New repository** → name `prc-website` → **Private** →
   do **not** add a README/.gitignore/licence.
2. In the project folder:

```bash
git remote add origin https://github.com/<your-username>/prc-website.git
git push -u origin main
```

If Git asks for a password, use a **Personal Access Token** (GitHub → Settings →
Developer settings → Personal access tokens → Fine-grained tokens → repo
contents: read/write) as the password.

> Only source is tracked (~64 files, under 1 MB). `media/` (admin uploads) and
> `website/static/website/images/` (the photo library) are **not** in git: they
> live in `~/prcapp` on the server and are left untouched by deploys. `venv/`,
> `dist/`, `staticfiles/` and `db.sqlite3` are ignored too.

---

## 2. Clone the repo on cPanel

cPanel → **Git™ Version Control** → **Create**:

- Clone a Repository: **Clone**
- Clone URL: `https://github.com/<your-username>/prc-website.git`
- Repository Path: `/home/pokharac/repositories/prc-website`
- Repository Name: `prc-website`

For a private repo, cPanel asks for credentials: GitHub username + the Personal
Access Token from step 1.

The clone must live **outside** the app root — `.cpanel.yml` copies files from
the clone into `~/prcapp`.

---

## 3. Configure the Python app (once)

cPanel → **Setup Python App**:

- Application root: `prcapp`
- Application URL: your domain
- Application startup file: `app.py`

Environment variables (these survive every deploy — never put DB credentials in
`config/settings.py`):

| Variable | Value |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | long random string |
| `DJANGO_ALLOWED_HOSTS` | `pokharacentre.org,www.pokharacentre.org` |
| `DJANGO_DB` | `mysql` |
| `DJANGO_DB_NAME` | `pokharac_prc` |
| `DJANGO_DB_USER` | `pokharac_admin` |
| `DJANGO_DB_PASSWORD` | your DB password |
| `DJANGO_SSL_REDIRECT` | `True` only after HTTPS works |

Generate the secret key locally:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 4. First deployment

1. cPanel → **Git Version Control** → `prc-website` → **Manage** →
   **Pull or Deploy** → **Update from Remote**, then **Deploy HEAD Commit**.
2. This runs `.cpanel.yml`, which copies `manage.py`, `app.py`,
   `passenger_wsgi.py`, `requirements.txt`, `prc_data.json`, `config/` and
   `website/` into `~/prcapp`. Images in `media/` and the static photo library
   are not in git and stay where they are; a brand-new server needs those
   uploaded separately (or use the zip package for the first install).
3. Verify:

```bash
ls ~/prcapp
# app.py  manage.py  config  website  media  requirements.txt  prc_data.json  passenger_wsgi.py
```

4. Terminal:

```bash
source /home/pokharac/virtualenv/prcapp/3.12/bin/activate
cd ~/prcapp
pip install -r requirements.txt          # required: cryptography was added
python manage.py migrate                 # applies website 0014-0016
python manage.py collectstatic --noinput
```

`prc_data.json` is only for a **fresh** database — on an existing site it would
duplicate content:

```bash
python manage.py loaddata prc_data.json  # fresh installs only
python manage.py createsuperuser         # if you have no admin login yet
```

5. Setup Python App → **Restart**, then check `/`, `/institution/`, `/events/`,
   `/admin/`.

If the app 500s, read `~/prcapp/stderr.log` (or Setup Python App → Logs) before
changing anything.

---

## 5. Routine updates

```bash
git add -A && git commit -m "Describe the change" && git push
```

Then in cPanel: **Git Version Control → Manage → Update from Remote → Deploy
HEAD Commit**, and in Terminal:

```bash
source /home/pokharac/virtualenv/prcapp/3.12/bin/activate
cd ~/prcapp
pip install -r requirements.txt   # only if requirements.txt changed
python manage.py migrate          # only if migrations were added
python manage.py collectstatic --noinput
```

and **Restart** the app. A restart is always required: Passenger caches Python
modules.

### Media uploads

Images uploaded through `/admin/` go to `~/prcapp/media/` and are **not** in
Git, same for `website/static/website/images/`. Deploys only copy files that
exist in the repo (`cp -u`), so both directories are never deleted or
overwritten. Do not run `git clean` in `~/prcapp`. Use cPanel backups or a
separate copy/rsync for those assets.

---

## 6. Notes and gotchas

- `.gitignore` excludes `settingsp.py` and `config/settings.production.py`
  because they contain live MySQL credentials. `config/settings.py` is safe:
  it only reads credentials from environment variables.
- Deleted files: `cp -Ru` copies new/changed files but does not delete files
  removed from the repo. If you delete a template, remove it on the server too.
- `collectstatic` must run after any static/template change; otherwise
  WhiteNoise raises `Missing staticfiles manifest entry` (a 500 on every page).
- Migrations are deliberately manual: if a migration fails halfway through a
  deploy, the code is still in place and can be fixed from the Terminal.
- To force a full re-copy (e.g. corrupted files), delete `~/prcapp/config` and
  `~/prcapp/website` **after taking a backup**, then Deploy HEAD Commit again.
