from django.utils import timezone
from django.views.generic import TemplateView, ListView
from django.db.models import F, ExpressionWrapper, IntegerField, Value
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Members, MemberPayment


class GymDashboardOveriew(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/gym_dashboard_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.today
        members = Members.objects.all()
        total_members_count = members.count()
        upcoming_renewals = MemberPayment.objects.filter(
                    expiration_date__year=now.year,
                    expiration_date__month=now.month
                ).count()
        # upcoming_renewals_members = MemberPayment.objects.filter(
        #     expiration_date__gte=today
        # ).annotate(
        #     days_left=ExpressionWrapper(
        #         F('expiration_date') - Value(today),
        #         output_field=IntegerField()
        #     )
        # )

        total_revenue = MemberPayment.objects.aggregate(total=Sum('amount'))['total'] or 0
        active_subscriptions = MemberPayment.objects.filter(
            expiration_date__gte=now.date()
        ).count()

        new_members = members.order_by('created_at')[:5]

        monthly_revenue = (
            MemberPayment.objects
            .annotate(month=TruncMonth('date_of_payment'))
            .values('month')
            .annotate(month_total=Sum('amount'))
        )

        # Calculate average
        if monthly_revenue:
            total_months = len(monthly_revenue)
            sum_months = sum(m['month_total'] for m in monthly_revenue)
            average_monthly_revenue = sum_months / total_months
        else:
            average_monthly_revenue = 0
        
        total_new_members = members.filter(
            created_at__year=now.year,
            created_at__month=now.month
        ).count()

        # print("upcoming_renewals_members", upcoming_renewals_members)
        context.update({
            "members": {
                'total_members_count': total_members_count,
                'total_new_members': total_new_members,
                "upcoming_renewals": upcoming_renewals,
                "new_members": new_members,
                # "upcoming_renewals_members": upcoming_renewals_members
            },
            "subscriptions": {
                "average_monthly_revenue": average_monthly_revenue,
                "active_subscriptions": active_subscriptions,
                "total_revenue": total_revenue
            }

        })
        return context

class MemberList(LoginRequiredMixin, ListView):
    template_name = 'dashboard/members_list.html'
    model = Members
    context_object_name = "members"

