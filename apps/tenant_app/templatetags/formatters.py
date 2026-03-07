from django import template

register = template.Library()

@register.filter
def naira(value):
    """Format number as Naira currency (₦12,345)."""
    try:
        return f"₦{value:,.0f}"
    except Exception:
        return value

@register.filter
def number(value, decimals=0):
    """Format number with commas, optional decimals (12,345 or 12,345.68)."""
    try:
        if decimals == 0:
            return f"{int(value):,}"
        else:
            return f"{float(value):,.{decimals}f}"
    except Exception:
        return value

@register.filter
def percentage(value, decimals=2):
    """Format a decimal/fraction as a percentage (0.25 -> 25.00%)."""
    try:
        return f"{value * 100:.{decimals}f}%"
    except Exception:
        return value