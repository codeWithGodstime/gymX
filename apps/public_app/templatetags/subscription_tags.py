from django import template
from apps.public_app.models import SubscriptionPlan  # your model for plans

register = template.Library()

@register.inclusion_tag("partials/subscription_cards.html")
def show_subscription_plans():
    plans = SubscriptionPlan.objects.all().order_by("amount")  # order as you like
    return {"plans": plans}