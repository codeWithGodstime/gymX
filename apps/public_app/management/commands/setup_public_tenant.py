from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context
from django.conf import settings
from apps.public_app.models import Gym, Domain


class Command(BaseCommand):
    help = 'Create public gym and localhost domain if they do not exist'

    def handle(self, *args, **options):
        host = settings.DOMAIN_HOST
        host = host.replace("http://", "").replace("https://", "").split(":")[0]
        with schema_context('public'):
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

            domain = Domain.objects.filter(
                domain=host,
                tenant=public_gym
            ).first()

            if not domain:
                self.stdout.write(f'Creating domain {host}...')
                Domain.objects.create(
                    domain=host,
                    tenant=public_gym,
                    is_primary=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created domain {host} for {public_gym.name}')
                )
            else:
                self.stdout.write(f'Domain {host} already exists for {public_gym.name}')