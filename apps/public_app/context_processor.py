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

    def number(amount, decimals=0):
        """
        Format number with comma separators and optional decimals
        Example: 12345 -> 12,345
                 12345.678, decimals=2 -> 12,345.68
        """
        try:
            if decimals == 0:
                return f"{int(amount):,}"
            else:
                return f"{float(amount):,.{decimals}f}"
        except Exception:
            return amount

    def percentage(value, decimals=2):
        """
        Format a decimal/fraction as percentage
        Example: 0.25 -> 25.00%
        """
        try:
            return f"{value * 100:.{decimals}f}%"
        except Exception:
            return value

    return {
        "today": today,
        "current_month": today.strftime("%B"),
        "current_year": today.year,
        "naira": naira,
        "number": number,
        "percentage": percentage,
    }