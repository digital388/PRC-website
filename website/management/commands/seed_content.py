"""
Imports all current hardcoded content into the database (idempotent — safe to re-run).
Images referenced by static paths are copied into MEDIA_ROOT so they become uploadable.
Run:  python manage.py seed_content
"""
import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from website import views as site_data
from website.models import (
    TeamMember, BoardMember, Partner, InstitutionProject, FundingItem,
    ProvinceProject, FlagshipProgram, YPGBatch, PastProject, YPGFellow, YPGFellowProfile,
    YPGTestimonial, ConstitutionProject, Event, Publication, BlogPost,
    GalleryPhoto, PageText,
)
from website.page_text_defaults import PAGE_TEXT_DEFAULTS


def media_file(static_ref):
    """Copy a 'website/images/...' static reference into MEDIA_ROOT; return the new relative name.
    Overwrites the destination when its contents differ from the static source."""
    if not static_ref:
        return None
    src = Path(settings.BASE_DIR) / "website" / "static" / static_ref
    if not src.is_file():
        return None
    dest = Path(settings.MEDIA_ROOT) / static_ref.split("website/images/", 1)[-1]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.read_bytes() != src.read_bytes():
        shutil.copyfile(src, dest)
    return dest.relative_to(settings.MEDIA_ROOT).as_posix()


def attach(obj, field, static_ref):
    name = media_file(static_ref)  # stage fresh bytes at MEDIA_ROOT/<name>
    if not name:
        return
    source = (Path(settings.MEDIA_ROOT) / name).read_bytes()  # keep bytes safe before deletes
    f = getattr(obj, field)
    ut = str(getattr(obj._meta.get_field(field), "upload_to", "") or "").strip("/")
    # Explicit final path: prepend upload_to unless the staged name already sits under it
    target = name if (not ut or name.startswith(ut + "/")) else f"{ut}/{name}"
    storage = f.storage
    if f.name and f.name != target and storage.exists(f.name):
        storage.delete(f.name)  # legacy upload stored under a different name
    if storage.exists(target):
        storage.delete(target)  # overwrite canonical slot; avoids random _XXXX suffixes
    setattr(f, "name", storage.save(target, ContentFile(source)))
    obj.save()


class Command(BaseCommand):
    help = "Seed the database with the site's current content"

    def handle(self, *args, **options):
        created = updated = 0

        def tally(model, obj, was_created):
            nonlocal created, updated
            if was_created:
                created += 1
            else:
                updated += 1

        # --- Team ---
        for i, m in enumerate(site_data.TEAM, start=1):
            obj, was = TeamMember.objects.update_or_create(
                slug=m["slug"],
                defaults=dict(
                    en_name=m["en_name"], np_name=m["np_name"],
                    category=m.get("category", TeamMember.Category.EXECUTIVE),
                    role_en=m["role_en"], role_np=m["role_np"],
                    title_en=m["title_en"], title_np=m["title_np"],
                    bio_en=m["bio_en"], bio_np=m["bio_np"], order=i,
                ),
            )
            attach(obj, "photo", m.get("photo") or f"website/images/team/t{i}.jpg")
            tally(TeamMember, obj, was)

        # --- Board of Directors ---
        for i, m in enumerate(site_data.BOARD, start=1):
            obj, was = BoardMember.objects.update_or_create(
                en_name=m["en_name"],
                defaults=dict(np_name=m["np_name"], role_en=m["role_en"], role_np=m["role_np"], order=i),
            )
            tally(BoardMember, obj, was)

        # --- Partners ---
        for i, p in enumerate(site_data.PARTNERS, start=1):
            obj, was = Partner.objects.update_or_create(
                en_name=p["en"],
                defaults=dict(np_name=p["np"], type_en=p["type_en"], type_np=p["type_np"],
                              since=p["since"], order=i),
            )
            attach(obj, "logo", p.get("logo", ""))
            tally(Partner, obj, was)

        # --- Institution projects ---
        for i, p in enumerate(site_data.INSTITUTION_PROJECTS, start=1):
            obj, was = InstitutionProject.objects.update_or_create(
                title=p["title"],
                defaults=dict(title_np=p.get("title_np", ""), type=p["type"], type_np=p.get("type_np", ""),
                              description=p["description"], description_np=p.get("description_np", ""), order=i),
            )
            tally(InstitutionProject, obj, was)

        # --- Funding items ---
        FundingItem.objects.all().delete()
        for i, (en, np) in enumerate(site_data.FUNDING_GENERAL, start=1):
            FundingItem.objects.create(category=FundingItem.Category.GENERAL, en=en, np=np, order=i)
        for i, (en, np) in enumerate(site_data.FUNDING_PROJECT, start=1):
            FundingItem.objects.create(category=FundingItem.Category.PROJECT, en=en, np=np, order=i)

        # --- Province projects ---
        for i, p in enumerate(site_data.PROVINCE_CURRENT_PROJECTS, start=1):
            obj, was = ProvinceProject.objects.update_or_create(
                code=p["code"],
                defaults=dict(name=p["name"], status=p["status"], detail=p.get("detail", ""),
                              link=p.get("link", ""), link_label=p.get("link_label", "View Details"), order=i),
            )
            tally(ProvinceProject, obj, was)

        # --- Flagship programs (Province page) ---
        for i, p in enumerate(site_data.FLAGSHIP_PROGRAMS, start=1):
            obj, was = FlagshipProgram.objects.update_or_create(
                title_en=p["title_en"],
                defaults=dict(
                    title_np=p["title_np"],
                    description_en=p["description_en"], description_np=p["description_np"],
                    link=site_data._flagship_link(p["link"]),
                    link_label_en=p["link_label_en"], link_label_np=p["link_label_np"],
                    order=i,
                ),
            )
            attach(obj, "image", p["image"])
            tally(FlagshipProgram, obj, was)

        # --- YPG batches ---
        YPGBatch.objects.all().delete()
        for i, b in enumerate(site_data.YPG_BATCHES, start=1):
            YPGBatch.objects.create(year=b[0], province_en=b[1], province_np=b[2],
                                    participation=b[3], ratio=b[4], order=i)

        # --- Past projects ---
        PastProject.objects.all().delete()
        for i, p in enumerate(site_data.PAST_PROJECTS, start=1):
            PastProject.objects.create(
                title=p["title"], cell=p.get("cell", ""), year=p["year"], partner=p["partner"],
                period=p.get("period", ""), summary=p.get("summary", ""), details=p.get("details", ""), order=i,
            )

        # --- YPG fellows & testimonials (optimized copies under pages/ypg/) ---
        if not YPGFellow.objects.exists():
            for f in site_data.YPG_FELLOWS:
                obj = YPGFellow.objects.create(cohort_en=f["cohort_en"], cohort_np=f["cohort_np"])
                attach(obj, "image", f["image"])
        if not YPGTestimonial.objects.exists():
            for i, t in enumerate(site_data.YPG_TESTIMONIALS, start=1):
                obj = YPGTestimonial.objects.create(order=i)
                attach(obj, "image", t)

        # --- YPG fellow profiles (the "Meet our Fellows" wall) ---
        valid_slugs = {f["id"] for f in site_data.YPG_ALL_FELLOWS}
        stale_profiles = YPGFellowProfile.objects.exclude(slug__in=valid_slugs)
        if stale_profiles.exists():
            self.stdout.write(f"Removing {stale_profiles.count()} stale YPG fellow profile(s)")
            stale_profiles.delete()
        for i, f in enumerate(site_data.YPG_ALL_FELLOWS, start=1):
            obj, was = YPGFellowProfile.objects.update_or_create(
                slug=f["id"],
                defaults=dict(
                    name_en=f["name_en"], name_np=f.get("name_np", ""),
                    year_en=f["year_en"], year_np=f.get("year_np", ""),
                    province_en=f["province_en"], province_np=f.get("province_np", ""),
                    cohort_en=f["cohort_en"], cohort_np=f.get("cohort_np", ""),
                    education_en=f.get("education_en", ""), education_np=f.get("education_np", ""),
                    post_grad_en=f.get("post_grad_en", ""), post_grad_np=f.get("post_grad_np", ""),
                    address_en=f.get("address_en", ""), address_np=f.get("address_np", ""),
                    current_engagement=f.get("current_engagement", ""),
                    bio_en=f.get("bio_en", ""), bio_np=f.get("bio_np", ""),
                    order=i,
                ),
            )
            if f.get("image"):
                attach(obj, "image", f["image"])
            tally(YPGFellowProfile, obj, was)

        # --- Constitution projects ---
        for i, p in enumerate(site_data.CONSTITUTION_PROJECTS, start=1):
            obj, was = ConstitutionProject.objects.update_or_create(
                name=p["name"],
                defaults=dict(name_np=p.get("name_np", ""), type=p["type"], type_np=p.get("type_np", ""),
                              description=p["description"], description_np=p.get("description_np", ""), order=i),
            )
            tally(ConstitutionProject, obj, was)

        # --- Events ---
        for i, e in enumerate(site_data.EVENTS, start=1):
            obj, was = Event.objects.update_or_create(
                title=e["title"],
                defaults=dict(
                    display_date=e["date"], day=e["day"], month=e.get("month", ""), year=e.get("year") or "",
                    type=e["type"], is_ongoing=e.get("status") == "ongoing",
                    description=e["description"], reach=e.get("reach", ""),
                    participants=e.get("participants", ""), link=e.get("link", ""), order=i,
                ),
            )
            if e.get("date_iso"):
                y, m, d = (int(x) for x in e["date_iso"].split("-"))
                obj.date_iso = obj.__class__._meta.get_field("date_iso").to_python(f"{y}-{m:02d}-{d:02d}")
                obj.save()
            attach(obj, "image", e.get("image", ""))
            tally(Event, obj, was)

        # --- Publications ---
        for i, p in enumerate(site_data.PUBLICATIONS, start=1):
            obj, was = Publication.objects.update_or_create(
                title=p["title"], year=p["year"],
                defaults=dict(partner=p["partner"], wing=p["wing"], link=p.get("link", "")),
            )
            attach(obj, "cover", p.get("image", ""))
            tally(Publication, obj, was)

        # --- Blogs ---
        for i, b in enumerate(site_data.BLOGS, start=1):
            obj, was = BlogPost.objects.update_or_create(
                title=b["title"],
                defaults=dict(title_np=b.get("title_np", ""), author=b["author"], author_np=b.get("author_np", ""),
                              date=b["iso"], date_np=b.get("date_np", "")),
            )
            tally(BlogPost, obj, was)

        # --- Galleries & hero slides ---
        gallery_map = [
            (GalleryPhoto.Section.HOME_GALLERY, site_data.GALLERY_PHOTOS),
            (GalleryPhoto.Section.CONSTITUTION_GALLERY, site_data.CONSTITUTION_PHOTOS),
            (GalleryPhoto.Section.HERO_HOME, site_data.HOME_PHOTOS),
            (GalleryPhoto.Section.HERO_INSTITUTION, site_data.INSTITUTION_PHOTOS),
            (GalleryPhoto.Section.HERO_PROVINCE, site_data.PROVINCE_PHOTOS),
            (GalleryPhoto.Section.HERO_CONSTITUTION, site_data.CONSTITUTION_RECENT_PHOTOS),
            (GalleryPhoto.Section.HERO_EVENTS, site_data.EVENT_BANNER_PHOTOS),
            (GalleryPhoto.Section.HERO_YPG, site_data.YPG_HERO),
        ]
        for section, refs in gallery_map:
            if not GalleryPhoto.objects.filter(section=section).exists():
                for i, ref in enumerate(refs, start=1):
                    obj = GalleryPhoto.objects.create(section=section, order=i, alt=Path(ref).stem)
                    attach(obj, "image", ref)

        # --- Page texts (headings & paragraphs) ---
        pt_created = pt_updated = 0
        for key, vals in PAGE_TEXT_DEFAULTS.items():
            page, _, label = key.partition(".")
            label = label.replace("_", " ").title()
            obj, was = PageText.objects.update_or_create(
                key=key,
                defaults=dict(page=page.title(), label=label,
                              text_en=vals["en"], text_np=vals.get("np", ""),
                              is_heading=not key.endswith("_body") and not key.endswith("_body_1") and not key.endswith("_body_2")),
            )
            pt_created += was
            pt_updated += not was

        self.stdout.write(self.style.SUCCESS(
            f"Seeded: {created} created, {updated} updated, page texts: {pt_created} created, {pt_updated} updated"))
