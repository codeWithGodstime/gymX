from django.conf import settings
from django.db import connection
from django.core.exceptions import DisallowedHost, PermissionDenied
from django.contrib.auth.middleware import get_user
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_domain_model

class CustomTenantMiddleware(TenantMainMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            connection.set_schema_to_public()
            hostname = self.hostname_from_request(request)
            domain_model = get_tenant_domain_model()
            
            tenant = self.get_tenant(domain_model, hostname)
            request.tenant = tenant
            connection.set_tenant(tenant)
            self.setup_url_routing(request)
                
        except (DisallowedHost):
            return self.no_tenant_found(request, hostname)
        
        if hasattr(request, 'session'):
            user = get_user(request)
            if user.is_authenticated and hasattr(user, 'tenant'):
                if user.tenant != request.tenant:
                    connection.set_schema_to_public()
                    return self.no_tenant_found(request, hostname)
        
        response = self.get_response(request)
        return response