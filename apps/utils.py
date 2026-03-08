from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator


class SubscriptionRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        print("Checking subscription status for tenant:", request.tenant)
        subscription = request.tenant.subscriptions.order_by('-start_date').first()
        print("Latest subscription found:", subscription, "Is active or trial?", subscription.is_active_or_trial if subscription else "No subscription")
        if not subscription or not subscription.is_active_or_trial:
            return redirect('subscription')  # Page to pick a plan
        return super().dispatch(request, *args, **kwargs)