from django.shortcuts import redirect
from django.conf import settings


class TenantLoginRequiredMiddleware:
    """
    If user is on a tenant domain and not authenticated,
    redirect to the public domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("TenantLoginRequiredMiddleware called for path:", request.path)
        # skip if already authenticated
        if request.user.is_authenticated:
            return self.get_response(request)
        
        # check if request is from tenant schema
        if hasattr(request, "tenant") and request.tenant.schema_name != "public":

            host = request.get_host()
            print("Should redirect to public domain. Current host:", host)

            # build redirect url to public domain
            redirect_url = f"{settings.DOMAIN_HOST}/accounts/login/"

            return redirect(redirect_url)

        return self.get_response(request)