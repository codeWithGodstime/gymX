# apps/core/context_processors.py

from datetime import date


def global_utils(request):
    today = date.today()

    def naira(amount):
        """
        Format number as Naira currency
        Example: 15000 -> ₦15,000
        """
        try:
            return f"₦{amount:,.0f}"
        except Exception:
            return amount

    return {
        "today": today,
        "current_month": today.strftime("%B"),  # March
        "current_year": today.year,             # 2026
        "naira": naira,
    }