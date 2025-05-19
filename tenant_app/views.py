from django.db import transaction
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import date, timedelta
from django.views.generic import TemplateView, ListView, CreateView, FormView
from django.db.models import OuterRef, Subquery
from django.db.models import F, ExpressionWrapper, IntegerField, Value
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import MemberCreationForm
from .models import Members, MemberPayment


class GymDashboardOveriew(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/gym_dashboard_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.today
        members = Members.objects.all()
        total_members_count = members.count()
        members_payment_expiration = MemberPayment.objects.filter(
                    expiration_date__year=now.year,
                    expiration_date__month=now.month
                )

        upcoming_renewals = members_payment_expiration.count()
        expiring_members = members_payment_expiration.select_related('member')

        for payment in expiring_members:
            payment.days_left = (payment.expiration_date - now).days

        total_revenue = MemberPayment.objects.aggregate(total=Sum('amount'))['total'] or 0
        active_subscriptions = MemberPayment.objects.filter(
            expiration_date__gte=now.date()
        ).count()

        latest_payment = MemberPayment.objects.filter(
            member=OuterRef('pk')
        ).order_by('-expiration_date')

        new_members = Members.objects.annotate(
            latest_expiration=Subquery(latest_payment.values('expiration_date')[:1])
        ).order_by('-created_at')[:5]

        monthly_revenue = (
            MemberPayment.objects
            .annotate(month=TruncMonth('date_of_payment'))
            .values('month')
            .annotate(month_total=Sum('amount'))
        )
        print(monthly_revenue, "Monthly_Revenue")

        # Calculate average
        if monthly_revenue:
            total_months = len(monthly_revenue)
            sum_months = sum(m['month_total'] for m in monthly_revenue)
            average_monthly_revenue = sum_months / total_months
        else:
            average_monthly_revenue = 0
        
        print(average_monthly_revenue, "Average")
        total_new_members = members.filter(
            created_at__year=now.year,
            created_at__month=now.month
        ).count()

        context.update({
            "members": {
                'total_members_count': total_members_count,
                'total_new_members': total_new_members,
                "upcoming_renewals": upcoming_renewals,
                "new_members": new_members,
                "expiring_members": expiring_members
            },
            "subscriptions": {
                "average_monthly_revenue": average_monthly_revenue,
                "active_subscriptions": active_subscriptions,
                "total_revenue": total_revenue
            }

        })
        return context

class MemberList(LoginRequiredMixin, ListView):
    model = Members
    template_name = 'dashboard/members_list.html'
    context_object_name = 'members'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('member_payments')

        for member in queryset:
            latest_payment = member.member_payments.order_by('-expiration_date').first()
            if latest_payment:
                member.expiration_date = latest_payment.expiration_date
                member.days_left = (latest_payment.expiration_date - date.today()).days
            else:
                member.expiration_date = None
                member.days_left = None
        return queryset

class NewMemberView(LoginRequiredMixin, FormView):
    template_name = "dashboard/add_members.html"
    form_class = MemberCreationForm
    success_url = reverse_lazy("members_list")

    @transaction.atomic
    def form_valid(self, form):
        name = form.cleaned_data['name']
        contact = form.cleaned_data['contact']
        member_type = form.cleaned_data['type']
        amount = form.cleaned_data['amount']
        today = timezone.now().date()

        # Create Member
        member = Members.objects.create(
            name=name,
            contact=contact,
            type=member_type
        )

        # Determine expiration
        if member_type == 'one-time':
            expiration_date = today
        else:  # monthly
            expiration_date = today + timedelta(days=30)

        # Create Payment
        MemberPayment.objects.create(
            member=member,
            amount=amount,
            date_of_payment=today,
            expiration_date=expiration_date,
            is_renewal=False
        )

        return super().form_valid(form)
