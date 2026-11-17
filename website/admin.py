from django.contrib import admin
from django.contrib.admin.decorators import display

from .models import (
    TeamMember, BoardMember, Partner, InstitutionProject, FundingItem,
    ProvinceProject, FlagshipProgram, YPGBatch, PastProject, YPGFellow, YPGFellowProfile,
    YPGTestimonial, ConstitutionProject, Event, Publication, BlogPost,
    GalleryPhoto, PageText,
)

admin.site.site_header = "Pokhara Research Centre — Administration"
admin.site.site_title = "PRC Admin"
admin.site.index_title = "Content management"
admin.site.site_url = "/"


class HideableAdmin(admin.ModelAdmin):
    """Content admin with a "Hidden" checkbox plus bulk hide/show actions.

    Hidden rows stay in the database and remain editable here, but every public
    page omits them — so editors can take an item down without deleting it.
    """
    actions = ("hide_selected", "show_selected")

    def get_list_display(self, request):
        return (*super().get_list_display(request), "is_hidden")

    def get_list_editable(self, request):
        return (*super().get_list_editable(request), "is_hidden")

    def get_list_filter(self, request):
        return (*super().get_list_filter(request), "is_hidden")

    @admin.action(description="Hide selected items from the website")
    def hide_selected(self, request, queryset):
        updated = queryset.update(is_hidden=True)
        self.message_user(request, f"{updated} item(s) hidden from the website.")

    @admin.action(description="Show selected items on the website")
    def show_selected(self, request, queryset):
        updated = queryset.update(is_hidden=False)
        self.message_user(request, f"{updated} item(s) shown on the website.")


@admin.register(TeamMember)
class TeamMemberAdmin(HideableAdmin):
    list_display = ("photo_tag", "en_name", "category", "role_en", "slug", "order")
    list_editable = ("order",)
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("en_name",)}
    search_fields = ("en_name", "np_name", "role_en")
    fieldsets = (
        (None, {"fields": ("en_name", "np_name", "slug", "category", "photo", "order", "is_hidden")}),
        ("Role", {"fields": ("role_en", "role_np", "title_en", "title_np")}),
        ("Biography", {"fields": ("bio_en", "bio_np"), "classes": ("collapse",)}),
    )

    @display(description="Photo")
    def photo_tag(self, obj):
        from django.utils.html import format_html
        if obj.photo:
            return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.photo.url)
        return "—"


@admin.register(BoardMember)
class BoardMemberAdmin(HideableAdmin):
    list_display = ("photo_tag", "en_name", "role_en", "order")
    list_editable = ("order",)
    search_fields = ("en_name", "np_name", "role_en")

    @display(description="Photo")
    def photo_tag(self, obj):
        from django.utils.html import format_html
        if obj.photo:
            return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.photo.url)
        return "—"


@admin.register(Partner)
class PartnerAdmin(HideableAdmin):
    list_display = ("logo_tag", "en_name", "type_en", "since", "order")
    list_editable = ("order",)
    search_fields = ("en_name", "np_name")
    list_filter = ("type_en",)

    @display(description="Logo")
    def logo_tag(self, obj):
        from django.utils.html import format_html
        if obj.logo:
            return format_html('<img src="{}" style="height:28px;" />', obj.logo.url)
        return "—"


@admin.register(Event)
class EventAdmin(HideableAdmin):
    list_display = ("image_tag", "title", "type", "display_date", "date_iso", "is_ongoing", "order")
    list_editable = ("order",)
    list_filter = ("type", "is_ongoing")
    search_fields = ("title", "description", "reach")
    fieldsets = (
        (None, {"fields": ("title", "image", "link", "order", "is_hidden")}),
        ("Date", {"fields": ("display_date", "date_iso", "day", "month", "year", "is_ongoing")}),
        ("Details", {"fields": ("type", "participants", "description", "reach")}),
    )

    @display(description="Image")
    def image_tag(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.image.url)
        return "—"


@admin.register(Publication)
class PublicationAdmin(HideableAdmin):
    list_display = ("cover_tag", "title", "partner", "wing", "year")
    list_filter = ("year", "partner")
    search_fields = ("title", "partner", "wing")

    @display(description="Cover")
    def cover_tag(self, obj):
        from django.utils.html import format_html
        if obj.cover:
            return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.cover.url)
        return "—"


@admin.register(BlogPost)
class BlogPostAdmin(HideableAdmin):
    list_display = ("title", "author", "date")
    search_fields = ("title", "author")


@admin.register(GalleryPhoto)
class GalleryPhotoAdmin(HideableAdmin):
    list_display = ("image_tag", "section", "alt", "order")
    list_editable = ("order",)
    list_filter = ("section",)
    search_fields = ("alt",)

    @display(description="Image")
    def image_tag(self, obj):
        from django.utils.html import format_html
        return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.image.url)


@admin.register(PageText)
class PageTextAdmin(admin.ModelAdmin):
    list_display = ("page", "label", "key", "is_heading", "text_en")
    list_display_links = ("label",)
    list_filter = ("page", "is_heading")
    search_fields = ("key", "label", "text_en", "text_np")
    ordering = ("page", "label")
    fieldsets = (
        (None, {"fields": ("page", "label", "key", "is_heading")}),
        ("Text", {"fields": ("text_en", "text_np")}),
    )


@admin.register(YPGFellowProfile)
class YPGFellowProfileAdmin(HideableAdmin):
    list_display = ("photo_tag", "name_en", "name_np", "year_en", "province_en", "cohort_en", "order")
    list_editable = ("order",)
    list_filter = ("year_en", "province_en")
    search_fields = ("name_en", "name_np", "education_en", "bio_en")
    fieldsets = (
        ("Identity", {"fields": ("slug", "name_en", "name_np", "image", "order", "is_hidden")}),
        ("Cohort", {"fields": ("year_en", "year_np", "province_en", "province_np", "cohort_en", "cohort_np")}),
        ("Education", {"fields": ("education_en", "education_np", "post_grad_en", "post_grad_np")}),
        ("Details", {"fields": ("address_en", "address_np", "current_engagement")}),
        ("Biography", {"fields": ("bio_en", "bio_np")}),
    )

    @display(description="Photo")
    def photo_tag(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:6px;" />', obj.image.url)
        return "—"


@admin.register(FlagshipProgram)
class FlagshipProgramAdmin(HideableAdmin):
    list_display = ("image_tag", "title_en", "link", "order")
    list_editable = ("order",)
    search_fields = ("title_en", "title_np", "description_en")
    fieldsets = (
        (None, {"fields": ("title_en", "title_np", "image", "order", "is_hidden")}),
        ("Description", {"fields": ("description_en", "description_np")}),
        ("Explore link", {"fields": ("link", "link_label_en", "link_label_np"), "classes": ("collapse",)}),
    )

    @display(description="Image")
    def image_tag(self, obj):
        from django.utils.html import format_html
        if obj.image:
            return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.image.url)
        return "—"


simple_lists = [
    (InstitutionProject, ("title", "type")),
    (FundingItem, ("category", "en")),
    (ProvinceProject, ("code", "name", "status")),
    (YPGBatch, ("year", "province_en", "participation")),
    (PastProject, ("title", "year", "partner", "period")),
    (YPGFellow, ("cohort_en",)),
    (YPGTestimonial, ()),
    (ConstitutionProject, ("name", "type")),
]
for model, cols in simple_lists:
    admin.site.register(model, type(f"{model.__name__}Admin", (HideableAdmin,), {
        "list_display": ("__str__", "order") + cols,
        "list_editable": ("order",),
    }))
