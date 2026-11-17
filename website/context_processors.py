"""
Context processor: exposes admin-editable page texts to all templates.

Usage in templates (dotted path mirrors the key):
    {{ pt.home.hero_title.en }}   ... English value
    {{ pt.home.hero_title.np }}   ... Nepali value

Values come from the PageText model (editable at /admin/); if an entry is
missing or blank, PAGE_TEXT_DEFAULTS supplies the original copy.
"""
from .page_text_defaults import PAGE_TEXT_DEFAULTS
from .models import PageText


class _Node:
    """
    Nested, template-friendly accessor over the page-text tree.

    Note: no __getitem__ — Django templates try dictionary lookup BEFORE
    attribute lookup, so a __getitem__ here would intercept 'en'/'np' and
    shadow the properties below.
    """
    __slots__ = ("_branches", "_leaf")

    def __init__(self, leaf=None):
        self._leaf = leaf if leaf is not None else {"en": "", "np": ""}
        self._branches = {}

    def branch(self, name):
        return self._branches.setdefault(name, _Node())

    def set_leaf(self, leaf):
        self._leaf = leaf

    @property
    def en(self):
        return self._leaf["en"]

    @property
    def np(self):
        return self._leaf["np"]

    def __getattr__(self, name):
        # Only called for names not in __slots__/properties (i.e. branch names)
        if name.startswith("_"):
            raise AttributeError(name)
        return self._branches.get(name, _Node())

    def __str__(self):
        return self.en


def page_texts(request):
    try:
        rows = {r.key: r for r in PageText.objects.all()}
    except Exception:
        rows = {}

    root = _Node()
    for key, default in PAGE_TEXT_DEFAULTS.items():
        parts = key.split(".")
        node = root
        for part in parts[:-1]:
            node = node.branch(part)
        row = rows.get(key)
        node.branch(parts[-1]).set_leaf({
            "en": (row.text_en if row and row.text_en else default["en"]),
            "np": (row.text_np if row and row.text_np else default["np"]),
        })

    # Also expose keys that exist in the DB but not in defaults
    for key, row in rows.items():
        parts = key.split(".")
        node = root
        for part in parts[:-1]:
            node = node.branch(part)
        last = node.branch(parts[-1])
        if not last.en and not last.np:
            last.set_leaf({"en": row.text_en, "np": row.text_np})

    return {"pt": root}
