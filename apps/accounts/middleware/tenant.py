from django.conf import settings
from django.db import connection
from django.core.exceptions import DisallowedHost
from django.contrib.auth.middleware import get_user
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_domain_model, remove_www


class CustomTenantMiddleware(TenantMainMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def hostname_from_request(self, request):
        hostname = remove_www(request.get_host())

        host = hostname.split(':')[0]  # Remove port if present
        return host.lower()

    def __call__(self, request):
        print("CustomTenantMiddleware was called:", request.path)
        try:
            connection.set_schema_to_public()
            hostname = self.hostname_from_request(request)
            domain_model = get_tenant_domain_model()
        
            tenant = self.get_tenant(domain_model, hostname)
            print("Tenant was found", tenant)
            request.tenant = tenant
            connection.set_tenant(tenant)
            self.setup_url_routing(request)
                
        except (DisallowedHost):
            return self.no_tenant_found(request, hostname)
        
        if hasattr(request, 'session'):
            user = get_user(request)
            if user.is_authenticated:
                if user.tenant != request.tenant:
                    connection.set_schema_to_public()
                    return self.no_tenant_found(request, hostname)
        
        response = self.get_response(request)
        return response
    