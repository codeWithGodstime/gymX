# apps/public_app/management/commands/reset_and_seed.py

from django.core.management.base import BaseCommand
from django_tenants.utils import schema_context, get_tenant_model
from django.db import connection
from apps.public_app.models import Domain, Gym
from apps.tenant_app.models import User, Members, MemberPayment, Activity
from datetime import date, timedelta
import random
import uuid

TenantModel = get_tenant_model()

class Command(BaseCommand):
    help = "Reset tenant schemas and seed two new gyms with members, payments, and activities"

    NEW_TENANTS = [
        {"schema_name": "alpha", "gym_name": "Alpha Gym", "admin_email": "admin@alpha.com"},
        {"schema_name": "beta", "gym_name": "Beta Gym", "admin_email": "admin@beta.com"}
    ]

    def drop_tenant_schema(self, schema_name):
        with connection.cursor() as cursor:
            self.stdout.write(f"Dropping schema {schema_name} if exists...")
            cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')

    def handle(self, *args, **options):
        self.stdout.write("=== Removing existing tenants and schemas ===")
        # 1. Drop schemas first
        for tenant in TenantModel.objects.exclude(schema_name='public'):
            schema_name = tenant.schema_name
            with connection.cursor() as cursor:
                self.stdout.write(f"Dropping schema {schema_name} if exists...")
                cursor.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')

        # 2. Delete tenant records safely AFTER drop
        for tenant in TenantModel.objects.exclude(schema_name='public'):
            # Skip deletion if schema was already gone (optional)
            tenant.delete()

        # Remove tenant domains except public
        Domain.objects.exclude(schema_name='public').delete()

        self.stdout.write("=== Creating new gyms and owners ===")
        for tenant_info in self.NEW_TENANTS:
            schema_name = tenant_info["schema_name"]
            gym_name = tenant_info["gym_name"]
            admin_email = tenant_info["admin_email"]

            # Create Gym tenant
            gym = Gym.objects.create(
                name=gym_name,
                schema_name=schema_name,
                auto_create_schema=True,
                active=True
            )

            # Create domain
            Domain.objects.create(
                domain=f"{schema_name}.gymx.local",
                tenant=gym,
                is_primary=True
            )

            self.stdout.write(f"Seeding data for {gym_name} ({schema_name})")
            with schema_context(schema_name):
                # Create admin user
                admin_user = User.objects.create_user(
                    username="admin",
                    email=admin_email,
                    password="admin123",
                    tenant=gym
                )

                # Seed members and payments
                members = []
                for i in range(10):
                    member = Members.objects.create(
                        name=f"Member {i+1}",
                        contact=f"080{i+1:07d}",
                        type=random.choice(["one-time", "monthly"])
                    )
                    members.append(member)

                    # Multiple payments per member
                    for _ in range(random.randint(2, 4)):
                        payment_date = date.today() - timedelta(days=random.randint(0, 90))
                        MemberPayment.objects.create(
                            member=member,
                            date_of_payment=payment_date,
                            amount=random.choice([10000, 15000, 20000]),
                            expiration_date=payment_date + timedelta(days=30),
                            is_renewal=random.choice([True, False])
                        )

                    # Multiple activities per member
                    activity_types = [
                        Activity.ActivityType.MEMBER_CREATED,
                        Activity.ActivityType.MEMBER_CHECKIN,
                        Activity.ActivityType.PAYMENT_SUCCESS,
                        Activity.ActivityType.PAYMENT_FAILED,
                        Activity.ActivityType.MEMBER_UPDATED
                    ]
                    for _ in range(random.randint(3, 7)):
                        act_type = random.choice(activity_types)
                        Activity.objects.create(
                            id=uuid.uuid4(),
                            user=admin_user,
                            activity_type=act_type,
                            description=f"{act_type.replace('_', ' ').title()} for {member.name}",
                            metadata={"member_id": str(member.id)}
                        )

            self.stdout.write(self.style.SUCCESS(f"Finished seeding {gym_name}"))