DATA = [
    {
        "name": "basic",
        "amount": 10000,
        "interval": "monthly",
        "paystack_plan_code": "PLN_p9yjll4wx9a56x3"
    },
    {
        "name": "premium",
        "amount": 95000,
        "interval": "yearly",
        "paystack_plan_code": "PLN_mebgjfsp68s5s6t"
    }
]

from django.core.management.base import BaseCommand
from apps.public_app.models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Create subscription plans'

    def handle(self, *args, **kwargs):
        # Delete existing plans
        SubscriptionPlan.objects.all().delete()
        self.stdout.write(self.style.WARNING('Deleted old subscription plans.'))
        
        # Create new plans
        for plan_data in DATA:
            SubscriptionPlan.objects.create(**plan_data)
        
        self.stdout.write(self.style.SUCCESS('Subscription plans created successfully.'))