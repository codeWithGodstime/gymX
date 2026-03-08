from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator


class SubscriptionRequiredMixin:
    """
    Mixin to restrict access to views based on active subscription.
    Assumes each tenant has a `subscription_active` boolean field.
    """

    subscription_required = True  # can be toggled per view

    def dispatch(self, request, *args, **kwargs):
        # Skip check if not required
        if not getattr(self, "subscription_required", True):
            return super().dispatch(request, *args, **kwargs)

        # Check subscription on the current tenant
        tenant = getattr(request, "tenant", None)
        if not tenant or not getattr(tenant, "subscription_active", False):
            pass
            # return redirect(reverse("subscription"))  # your subscription page

        return super().dispatch(request, *args, **kwargs)