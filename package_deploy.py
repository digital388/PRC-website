"""
Package the PRC website for upload to cPanel (Nest Nepal Django hosting).

Creates a zip containing ONLY the files the server needs, with files at the
zip root so you can extract directly into the Application Root folder.

Usage:
    python package_deploy.py                 # -> dist/prc_deploy_YYYYMMDD_HHMM.zip
    python package_deploy.py --out my.zip    # custom output path
    python package_deploy.py --with-sqlite   # also ship db.sqlite3 (dev DB; not used on MySQL)
    python package_deploy.py --all-media     # include every media file (default: only
                                             # the files referenced by the database)

Only files the cPanel host actually uses are shipped. Excluded automatically:
  - staticfiles/          (the server regenerates it with `collectstatic`)
  - db.sqlite3            (production uses MySQL; content comes from prc_data.json)
  - website/tests.py      (never run in production)
  - website/management/   (local-only commands; the server imports content with
                           `loaddata prc_data.json`)
Media is filtered to DB-referenced files by default, which keeps the zip small
(upload duplicates are skipped).
"""
import argparse
import os
import re
import sys
import time
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent

# Top-level files that must ship
ROOT_FILES = ["manage.py", "app.py", "requirements.txt", "prc_data.json", "passenger_wsgi.py"]

# Dev-only: the local SQLite database. Production runs on MySQL, so it is not
# shipped by default; opt in with --with-sqlite.
SQLITE_DB = "db.sqlite3"

# Folders that ship entirely (minus the excludes below)
FOLDERS = ["config", "website", "media"]

# Anything matching these is skipped, wherever it appears
EXCLUDE_DIRS = {"__pycache__", "staticfiles", "venv", ".git", ".idea", ".vscode", "node_modules", "migrations_backup"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".log", ".zip", ".sqlite3-journal", ".heic"}
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini", "package_deploy.py"}

# Dev-only paths (relative to the project root) that the cPanel host never uses.
DEV_ONLY_FILES = {"website/tests.py", "config/settings.production.py"}
DEV_ONLY_DIRS = ("website/management",)


def skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS


def skip_file(path: Path) -> bool:
    return path.name in EXCLUDE_NAMES or path.suffix.lower() in EXCLUDE_SUFFIXES


def is_dev_only(rel: Path) -> bool:
    posix = rel.as_posix()
    if posix in DEV_ONLY_FILES:
        return True
    return any(posix == d or posix.startswith(d + "/") for d in DEV_ONLY_DIRS)


def db_referenced_media(project: Path) -> set | None:
    """Return (media_refs, static_refs) used by the live site/DB.
    media_refs: paths relative to media/ that the DB references.
    static_refs: paths relative to website/static/ referenced by code or needed
                 as fallbacks (gallery model empty). None if Django setup fails."""
    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        os.chdir(project)
        import django
        django.setup()
        from django.db import models as djm
        from website import models as m
        from website.views import YPG_FELLOWS
    except Exception as e:
        print(f"WARNING: could not query the database ({e}); including ALL media/static files.")
        return None

    media_refs = set()
    content_models = [getattr(m, n) for n in dir(m) if isinstance(getattr(m, n), type) and issubclass(getattr(m, n), djm.Model)]
    for model in content_models:
        if model._meta.abstract or model._meta.proxy:
            continue
        file_fields = [f for f in model._meta.get_fields() if isinstance(f, djm.FileField)]
        if not file_fields:
            continue
        for obj in model.objects.all():
            for f in file_fields:
                val = getattr(obj, f.name)
                if val and val.name:
                    media_refs.add(val.name)

    # Static fallbacks needed if the YPGFellow (gallery) table is ever empty
    static_refs = {f"website/images/{f['image']}" for f in YPG_FELLOWS}

    # Every static path literally referenced in code/templates ({% static '...' %}, static('...'))
    patterns = [
        re.compile(r"\{%\s*static\s+['\"]([^'\"]+)['\"]"),
        re.compile(r"static\(\s*['\"]([^'\"]+)['\"]\s*\)"),
    ]
    scan_roots = [project / "website" / "templates", project / "website", project / "config"]
    for root in scan_roots:
        for py_html in root.rglob("*"):
            if py_html.suffix.lower() not in (".py", ".html") or not py_html.is_file():
                continue
            if any(part in EXCLUDE_DIRS for part in py_html.parts):
                continue
            text = py_html.read_text(encoding="utf-8", errors="ignore")
            for pat in patterns:
                static_refs.update(m.group(1) for m in pat.finditer(text))
    return media_refs, static_refs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None, help="output zip path (default: dist/prc_deploy_<timestamp>.zip)")
    ap.add_argument("--with-sqlite", action="store_true", help="also ship db.sqlite3 (dev database; not used on MySQL)")
    ap.add_argument("--all-media", action="store_true", help="include every media file, not just DB-referenced ones")
    args = ap.parse_args()

    # ---- pre-flight checks -------------------------------------------------
    problems = []
    required = list(ROOT_FILES)
    if args.with_sqlite:
        required.append(SQLITE_DB)
    for f in required:
        if not (PROJECT / f).is_file():
            problems.append(f"missing required file: {f}")
    for d in FOLDERS:
        if not (PROJECT / d).is_dir():
            problems.append(f"missing required folder: {d}/")
    if problems:
        print("CANNOT PACKAGE:")
        for p in problems:
            print("  -", p)
        return 1

    stamp = time.strftime("%Y%m%d_%H%M")
    out = Path(args.out) if args.out else PROJECT / "dist" / f"prc_deploy_{stamp}.zip"
    out.parent.mkdir(parents=True, exist_ok=True)

    media_filter = static_filter = None
    if not args.all_media:
        result = db_referenced_media(PROJECT)
        if result is not None:
            media_filter, static_filter = result
            print(f"Media filter: {len(media_filter)} DB-referenced files; "
                  f"static filter: {len(static_filter)} code-referenced files "
                  "(use --all-media to include everything)")

    CODE_ASSET_SUFFIXES = {".css", ".js", ".woff", ".woff2", ".ttf", ".otf", ".svg", ".ico", ".txt", ".webmanifest", ".json"}

    included = 0
    total_bytes = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in required:
            zf.write(PROJECT / f, f)
            included += 1
            total_bytes += (PROJECT / f).stat().st_size

        for folder in FOLDERS:
            for path in (PROJECT / folder).rglob("*"):
                if path.is_dir():
                    continue
                rel = path.relative_to(PROJECT)
                if any(skip_dir(part) for part in rel.parts[:-1]) or skip_file(path):
                    continue
                if is_dev_only(rel):
                    continue
                if folder == "media" and media_filter is not None:
                    if rel.relative_to("media").as_posix() not in media_filter:
                        continue
                if folder == "website" and static_filter is not None and rel.parts[0:2] == ("website", "static"):
                    rel_static = rel.relative_to("website/static").as_posix()
                    in_static = rel_static in static_filter
                    is_code_asset = path.suffix.lower() in CODE_ASSET_SUFFIXES
                    if not (in_static or is_code_asset):
                        continue
                zf.write(path, rel.as_posix())
                included += 1
                total_bytes += path.stat().st_size

    zip_kb = out.stat().st_size / 1024
    src_mb = total_bytes / (1024 * 1024)
    print(f"Created: {out}")
    print(f"Files: {included}  |  original size: {src_mb:.1f} MB  |  zip size: {zip_kb:.0f} KB")
    print()
    print("Upload checklist (cPanel, MySQL database):")
    print("  1. Upload this zip and EXTRACT into the Application Root (e.g. ~/prcapp)")
    print("     -> manage.py should end up at prcapp/manage.py")
    print("  2. cPanel > MySQL Database Wizard: create DB + user (SAVE the password).")
    print("     IMPORTANT: choose utf8mb4 collation (utf8mb4_unicode_ci) for Nepali text.")
    print("  3. Setup Python App: startup file = app.py, then Run pip install (requirements.txt)")
    print("  4. Point the app at the database -- EITHER fill DB_NAME / DB_USER /")
    print("     DB_PASSWORD in the DATABASE SETUP block at the top of config/settings.py")
    print("     OR add these env vars on the app (env vars win):")
    print("         DJANGO_DEBUG=False")
    print("         DJANGO_SECRET_KEY=<long random string>")
    print("         DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com")
    print("         DJANGO_DB=mysql")
    print("         DJANGO_DB_NAME=<cpaneluser_prc>")
    print("         DJANGO_DB_USER=<cpaneluser_prc>")
    print("         DJANGO_DB_PASSWORD=<the password from step 2>")
    print("  5. Terminal (activate the app's virtualenv first):")
    print("         python manage.py migrate")
    print("         python manage.py loaddata prc_data.json")
    print("         python manage.py createsuperuser")
    print("         python manage.py collectstatic --noinput")
    print("  6. Restart the app. Then enable AutoSSL and add env var DJANGO_SSL_REDIRECT=True.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
