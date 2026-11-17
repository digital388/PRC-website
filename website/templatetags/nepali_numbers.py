"""
Template filters for bilingual numeral rendering.

Usage:
    {% load nepali_numbers %}
    <span class="numeral en-ne">{{ value|en_ne }}</span>
Renders both systems as spans; CSS (.en/.np visibility) picks the right one,
so numbers convert exactly like every other word on the site — no JS needed.
"""
from django import template

EN = "0123456789"
NE = "०१२३४५६७८९"
_TRANS = str.maketrans(EN, NE)

register = template.Library()


@register.filter
def en_ne(value):
    """Return a string where every digit is doubled into EN + NE span pair."""
    s = str(value)
    out = []
    for ch in s:
        if ch in EN:
            i = EN.index(ch)
            out.append(
                f'<span class="en">{ch}</span><span class="np">{NE[i]}</span>'
            )
        else:
            out.append(ch)
    return "".join(out)


@register.filter
def ne(value):
    """Convert all digits in a string to Devanagari numerals (plain text)."""
    return str(value).translate(_TRANS)
