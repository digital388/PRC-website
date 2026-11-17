"""
Swap the 'Meet our Fellows' portrait wall to the uploaded passport photos.

Reads the photos dropped into media/ypg/YPG Fellow indivisual/ (ready/ wins
over needs_review/ when a fellow has both) and matches them to YPGFellowProfile
rows by name. Each fellow's existing image file is overwritten in place — both
the media copy and its static source copy — so the database, seed_content
re-runs and deploys all stay consistent. Fellows without an uploaded photo
keep their current portrait.

Run:  python manage.py update_fellow_portraits
"""
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from website.models import YPGFellowProfile

UPLOAD_DIR = Path(settings.MEDIA_ROOT) / "ypg" / "YPG Fellow indivisual"
# Search order: first folder that contains a fellow's photo wins
SUBDIRS = ["ready", "needs_review"]
PHOTO_SUFFIXES = {".jpg", ".jpeg", ".png"}


def norm(name):
    """Normalize a fellow name / file stem for matching: 'Chandra kala Ghale' -> 'chandra_kala_ghale'."""
    return name.strip().lower().replace(" ", "_")


class Command(BaseCommand):
    help = (
        "Replace fellow portraits on the YPG 'Meet our Fellows' wall with the uploaded "
        "passport photos (in-place file swap; no database changes)."
    )

    def handle(self, *args, **options):
        # Index uploaded photos: normalized file stem -> source path
        photos = {}
        for sub in SUBDIRS:
            folder = UPLOAD_DIR / sub
            if not folder.is_dir():
                continue
            for f in sorted(folder.iterdir()):
                if f.suffix.lower() in PHOTO_SUFFIXES:
                    photos.setdefault(norm(f.stem), f)

        if not photos:
            self.stdout.write(self.style.WARNING(f"No photos found under {UPLOAD_DIR}"))
            return

        upload_to = str(YPGFellowProfile._meta.get_field("image").upload_to).strip("/")
        updated, skipped, problems = [], [], []

        for p in YPGFellowProfile.objects.all().order_by("order"):
            src = photos.get(norm(p.name_en))
            if not src:
                skipped.append(p.name_en)
                continue
            if not p.image or not p.image.name:
                problems.append(f"{p.name_en}: profile has no image path; skipping")
                continue

            # Overwrite the media copy the DB points at
            media_dest = Path(settings.MEDIA_ROOT) / p.image.name
            media_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, media_dest)

            # Keep the static source copy in sync so re-running seed_content
            # (which re-attaches images from static) doesn't revert the portraits
            rel = p.image.name
            if upload_to and rel.startswith(upload_to + "/"):
                static_dest = (
                    Path(settings.BASE_DIR) / "website" / "static" / "website" / "images" / rel[len(upload_to) + 1:]
                )
                if static_dest.is_file():
                    shutil.copyfile(src, static_dest)
            updated.append(p.name_en)

        self.stdout.write(self.style.SUCCESS(f"Updated {len(updated)} portrait(s) from the uploaded photos"))
        if skipped:
            self.stdout.write(f"Kept current photo for {len(skipped)} fellow(s) with no upload match:")
            for n in skipped:
                self.stdout.write(f"  - {n}")
        for msg in problems:
            self.stdout.write(self.style.WARNING(msg))
