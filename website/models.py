from django.db import models


class OrderedListModel(models.Model):
    """Base for content that appears in a curated order on the site."""
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first")
    is_hidden = models.BooleanField(default=False, verbose_name="Hidden", help_text="Hide from the public site without deleting it")

    class Meta:
        abstract = True
        ordering = ["order", "id"]

    def __str__(self):
        return getattr(self, "title", None) or getattr(self, "en_name", None) or getattr(self, "name", None) or f"{self.__class__.__name__} #{self.pk}"


# ---------- Editable page copy ----------

class PageText(models.Model):
    """
    Editable page copy (headings, paragraphs, labels) keyed by a stable slug.
    Each entry holds EN + NE values; templates fall back to their defaults
    when an entry is missing, so the site works even with an empty table.
    """
    key = models.CharField(max_length=50, unique=True, help_text="Stable identifier used by templates, e.g. 'home.hero_title'. Dots are allowed because the key is a dotted path, not a URL slug.")
    page = models.CharField(max_length=40, help_text="Groups entries by page in the admin, e.g. 'Home'")
    label = models.CharField(max_length=120, help_text="Human-friendly name shown in the admin")
    text_en = models.TextField(blank=True)
    text_np = models.TextField(blank=True)
    is_heading = models.BooleanField(default=False, help_text="Headings render without HTML paragraphs")

    class Meta:
        ordering = ["page", "key"]

    def __str__(self):
        return f"{self.page} — {self.label}"


# ---------- Institution page ----------

class TeamMember(OrderedListModel):
    class Category(models.TextChoices):
        EXECUTIVE = "executive", "Executive"
        ADVISOR = "advisor", "Advisor"
        RESEARCH_FELLOW = "research_fellow", "Research Fellow"

    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.EXECUTIVE, db_index=True)
    en_name = models.CharField(max_length=120)
    np_name = models.CharField(max_length=120)
    role_en = models.CharField(max_length=160)
    role_np = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160, blank=True)
    title_np = models.CharField(max_length=160, blank=True)
    bio_en = models.TextField(blank=True)
    bio_np = models.TextField(blank=True)
    photo = models.ImageField(upload_to="team/", blank=True)

    class Meta(OrderedListModel.Meta):
        pass


class BoardMember(OrderedListModel):
    """A member of the governing board, listed above the Team section on the Institution page."""
    en_name = models.CharField(max_length=120)
    np_name = models.CharField(max_length=120)
    role_en = models.CharField(max_length=160, help_text='e.g. "Chairperson"')
    role_np = models.CharField(max_length=160)
    photo = models.ImageField(upload_to="board/", blank=True)

    class Meta(OrderedListModel.Meta):
        verbose_name = "Board Member"
        verbose_name_plural = "Board Members"


class Partner(OrderedListModel):
    class Meta(OrderedListModel.Meta):
        pass

    en_name = models.CharField(max_length=160)
    np_name = models.CharField(max_length=160)
    type_en = models.CharField(max_length=80, blank=True)
    type_np = models.CharField(max_length=80, blank=True)
    since = models.CharField(max_length=20, help_text='e.g. "A.D 2019"')
    logo = models.ImageField(upload_to="partners/", blank=True, help_text="Leave empty to show the partner's initials instead")


class InstitutionProject(OrderedListModel):
    title = models.CharField(max_length=80)
    title_np = models.CharField(max_length=120, blank=True)
    type = models.CharField(max_length=80, blank=True)
    type_np = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    description_np = models.TextField(blank=True)


class FundingItem(OrderedListModel):
    class Category(models.TextChoices):
        GENERAL = "general", "General sources of funding"
        PROJECT = "project", "Project based grants"

    category = models.CharField(max_length=10, choices=Category.choices)
    en = models.CharField(max_length=160)
    np = models.CharField(max_length=160)


# ---------- Province page ----------

class ProvinceProject(OrderedListModel):
    class Status(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        PLANNED = "planned", "Planned"

    code = models.CharField(max_length=12)
    name = models.CharField(max_length=160)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLANNED)
    detail = models.CharField(max_length=250, blank=True)
    link = models.URLField(blank=True)
    link_label = models.CharField(max_length=40, blank=True, default="View Details")


class FlagshipProgram(OrderedListModel):
    """A card in the 'Our Flagship Programs' grid on the Province page.
    The page falls back to the two built-in cards in views.py when this table is empty."""
    title_en = models.CharField(max_length=160)
    title_np = models.CharField(max_length=160, blank=True)
    description_en = models.TextField(blank=True)
    description_np = models.TextField(blank=True)
    image = models.ImageField(upload_to="flagship/", help_text="Image shown in the card")
    link = models.CharField(max_length=200, blank=True, help_text='Optional "Explore" link, e.g. /province/ypg-fellowship/ or https://…')
    link_label_en = models.CharField(max_length=40, blank=True, default="Explore")
    link_label_np = models.CharField(max_length=40, blank=True, default="थप हेर्नुहोस्")

    class Meta(OrderedListModel.Meta):
        verbose_name = "Flagship Program"
        verbose_name_plural = "Flagship Programs"


class YPGBatch(OrderedListModel):
    year = models.CharField(max_length=10, help_text='e.g. "2020/21"')
    province_en = models.CharField(max_length=40)
    province_np = models.CharField(max_length=40)
    participation = models.CharField(max_length=60, help_text='e.g. "6 Male, 6 Female"')
    ratio = models.CharField(max_length=10, help_text='e.g. "1:1"')


class PastProject(OrderedListModel):
    """A completed project on the Province page's Past Projects timeline.
    The page falls back to the hardcoded record in project_record_data.py when this table is empty."""
    title = models.CharField(max_length=200)
    cell = models.CharField(max_length=40, blank=True, help_text='Optional internal cell code, e.g. "PA:Gandaki"')
    year = models.CharField(max_length=10, help_text="Start year, used to order the timeline")
    partner = models.CharField(max_length=250, blank=True)
    period = models.CharField(max_length=120, blank=True, help_text='Free-text period shown on the node, e.g. "June 1 – December 10, 2023"')
    summary = models.TextField(blank=True, help_text="Short line shown on the card")
    details = models.TextField(blank=True, help_text="Longer objective / activities text revealed by the Details toggle")


class YPGFellow(OrderedListModel):
    cohort_en = models.CharField(max_length=60, help_text='e.g. "Gandaki 2022-23"')
    cohort_np = models.CharField(max_length=60, blank=True)
    image = models.ImageField(upload_to="ypg/fellows/")

    class Meta(OrderedListModel.Meta):
        verbose_name = "YPG Cohort Photo (gallery)"
        verbose_name_plural = "YPG Cohort Photos (gallery)"


class YPGFellowProfile(OrderedListModel):
    """A fellow shown in the 'Meet our Fellows' portrait wall on the YPG page.
    The page falls back to the hardcoded list in views.py when this table is empty."""
    slug = models.SlugField(unique=True, help_text="Stable identifier, e.g. 'fellow-01'")
    name_en = models.CharField(max_length=120)
    name_np = models.CharField(max_length=120, blank=True)
    year_en = models.CharField(max_length=10, help_text='Cohort year, e.g. "2023-24" — used by the year filter tabs')
    year_np = models.CharField(max_length=10, blank=True)
    province_en = models.CharField(max_length=40, help_text='e.g. "Gandaki" — used by the province filter buttons')
    province_np = models.CharField(max_length=40, blank=True)
    cohort_en = models.CharField(max_length=60, help_text='e.g. "Gandaki 2023-24"')
    cohort_np = models.CharField(max_length=60, blank=True)
    education_en = models.CharField(max_length=200, blank=True)
    education_np = models.CharField(max_length=200, blank=True)
    post_grad_en = models.CharField(max_length=200, blank=True)
    post_grad_np = models.CharField(max_length=200, blank=True)
    address_en = models.CharField(max_length=120, blank=True, help_text='Home district, e.g. "Kaski"')
    address_np = models.CharField(max_length=120, blank=True)
    current_engagement = models.TextField(blank=True, help_text='Current role / affiliation, e.g. "Student" or "Research Associate, PRC"')
    bio_en = models.TextField(blank=True)
    bio_np = models.TextField(blank=True)
    image = models.ImageField(upload_to="ypg/fellow_profiles/", help_text="Portrait photo shown on the wall tile and in the pop-up")

    class Meta(OrderedListModel.Meta):
        verbose_name = "YPG Fellow Profile"
        verbose_name_plural = "YPG Fellow Profiles"


class YPGTestimonial(OrderedListModel):
    image = models.ImageField(upload_to="ypg/testimonials/")


# ---------- Constitution page ----------

class ConstitutionProject(OrderedListModel):
    name = models.CharField(max_length=120)
    name_np = models.CharField(max_length=120, blank=True)
    type = models.CharField(max_length=80, blank=True)
    type_np = models.CharField(max_length=80, blank=True)
    description = models.TextField(blank=True)
    description_np = models.TextField(blank=True)


# ---------- Events page ----------

class Event(OrderedListModel):
    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="events/", blank=True)
    display_date = models.CharField(max_length=80, help_text='Free-text shown on the card, e.g. "July 13, 2026" or "Ongoing · Virtual"')
    date_iso = models.DateField(null=True, blank=True, help_text="Real date used for sorting and Upcoming/Completed classification")
    day = models.CharField(max_length=10, help_text="Big date column, e.g. 13 / TBA / Live")
    month = models.CharField(max_length=10, blank=True, help_text='e.g. "Jul" or "2083" or "Virtual"')
    year = models.CharField(max_length=10, blank=True)
    type = models.CharField(max_length=60, help_text='e.g. Dialogue, Exhibition, Report Launch')
    is_ongoing = models.BooleanField(default=False, help_text="Marks the event as Happening now")
    description = models.TextField(blank=True)
    reach = models.TextField(blank=True, help_text="Reach & stakeholders (revealed by Read More)")
    participants = models.CharField(max_length=60, blank=True, help_text='e.g. "94 participants"')
    link = models.URLField(blank=True)


# ---------- Publications page ----------

class Publication(OrderedListModel):
    title = models.CharField(max_length=250)
    partner = models.CharField(max_length=120)
    wing = models.CharField(max_length=120, help_text='e.g. "PG:Ministry of Economic Affairs"')
    year = models.CharField(max_length=10)
    cover = models.ImageField(upload_to="publications/", blank=True)
    link = models.URLField(blank=True)

    class Meta(OrderedListModel.Meta):
        ordering = ["-year", "title"]


# ---------- Archives page ----------

class BlogPost(OrderedListModel):
    title = models.CharField(max_length=250)
    title_np = models.CharField(max_length=250, blank=True)
    author = models.CharField(max_length=120)
    author_np = models.CharField(max_length=120, blank=True)
    date = models.DateField()
    date_np = models.CharField(max_length=60, blank=True)

    class Meta(OrderedListModel.Meta):
        ordering = ["-date"]


# ---------- Photo galleries & hero slides ----------

class GalleryPhoto(OrderedListModel):
    class Section(models.TextChoices):
        HOME_GALLERY = "home_gallery", "Home — Our Work in Pictures"
        CONSTITUTION_GALLERY = "constitution_gallery", "Constitution — From Our Programs"
        HERO_HOME = "hero_home", "Hero — Home"
        HERO_INSTITUTION = "hero_institution", "Hero — Institution"
        HERO_PROVINCE = "hero_province", "Hero — Province"
        HERO_CONSTITUTION = "hero_constitution", "Hero — Constitution"
        HERO_EVENTS = "hero_events", "Hero — Events"
        HERO_YPG = "hero_ypg", "Hero — YPG Fellowship"

    section = models.CharField(max_length=30, choices=Section.choices, db_index=True)
    image = models.ImageField(upload_to="gallery/")
    alt = models.CharField(max_length=160, blank=True)
