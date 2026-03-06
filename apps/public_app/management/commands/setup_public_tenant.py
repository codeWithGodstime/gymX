from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from apps.public_app.models import Gym, Domain


class Command(BaseCommand):
    help = 'Create public gym and localhost domain if they do not exist'

    def handle(self, *args, **options):
        # Switch to public schema to create the tenant
        with schema_context('public'):
            # Check if public gym exists
            public_gym = Gym.objects.filter(schema_name='public').first()

            if not public_gym:
                self.stdout.write('Creating public gym...')
                public_gym = Gym.objects.create(
                    name='Public Gym',
                    schema_name='public',
                    active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created public gym: {public_gym.name}')
                )
            else:
                self.stdout.write(f'Public gym already exists: {public_gym.name}')

            # Check if localhost domain exists for this gym
            localhost_domain = Domain.objects.filter(
                domain='localhost',
                tenant=public_gym
            ).first()

            if not localhost_domain:
                self.stdout.write('Creating localhost domain...')
                localhost_domain = Domain.objects.create(
                    domain='localhost',
                    tenant=public_gym,
                    is_primary=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created localhost domain for {public_gym.name}')
                )
            else:
                self.stdout.write(f'Localhost domain already exists for {public_gym.name}')