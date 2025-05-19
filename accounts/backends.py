# accounts/backends.py
from django.contrib.auth import get_user_model
from allauth.account.auth_backends import AuthenticationBackend
from django_tenants.utils import schema_context, get_public_schema_name


class TenantAwareAuthBackend(AuthenticationBackend):
    def authenticate(self, request, **credentials):
        user = super().authenticate(request, **credentials)
        
        if not user:
            return None

        with schema_context(get_public_schema_name()):
            if not hasattr(user, 'tenant') or not user.tenant:
                return None

            if not self._verify_domain_access(user, request):
                return None
                
        return user

    def _verify_domain_access(self, user, request):
        """Verify user has access to the requested domain"""
        from public_app.models import Domain
        hostname = request.get_host().split(':')[0]
      
        return Domain.objects.filter(
            tenant=user.tenant,
            domain=hostname
        ).exists()