from django import template

register = template.Library()


@register.filter
def prefixed_id(value, prefix="tag_modal"):
    """Return a DOM-friendly id using a prefix and suffix."""
    prefix_str = str(prefix).strip() if prefix is not None else "tag_modal"
    if not prefix_str:
        prefix_str = "tag_modal"

    if value is None:
        return prefix_str

    suffix_str = str(value).strip()
    if not suffix_str:
        return prefix_str

    return f"{prefix_str}_{suffix_str}".replace(" ", "-")
