from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import date, timedelta
from django.views.generic import TemplateView, ListView, FormView, View
from django.views.generic.edit import UpdateView
from django_tenants.utils import tenant_context
from django.db.models import OuterRef, Subquery
from django.db.models import F, ExpressionWrapper, IntegerField, Value, Count, Sum, Avg, DurationField, Min, Max
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin
from .service import DashboardMetricsService, ActivityService

from .forms import NewMemberForm
from .models import Member, MemberPayment, Activity



class GymDashboardOveriew(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/gym_dashboard_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
    
def dashboard_analytics(request):
    filter_type = request.GET.get("filter", "month")
    today = date.today()

    # Determine start and end dates based on filter
    if filter_type == "today":
        start_date = end_date = today
    elif filter_type == "month":
        start_date = today.replace(day=1)
        end_date = today
    elif filter_type == "year":
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        start_date = end_date = None  # fallback: all time

    # Get metrics dynamically
    metrics = DashboardMetricsService.get_dashboard_metrics(start_date, end_date)

    # Optional: calculate growth vs previous period
    def calculate_growth(metric_fn, start, end, period_delta):
        prev_start = start - period_delta
        prev_end = end - period_delta
        current = metric_fn(start, end)
        previous = metric_fn(prev_start, prev_end)
        if previous == 0:
            return 0
        return round(((current - previous) / previous) * 100, 1)

    from datetime import timedelta

    members_growth = calculate_growth(
        DashboardMetricsService.get_active_members_count,
        start_date, end_date,
        timedelta(days=(end_date - start_date).days + 1)
    )
    revenue_growth = calculate_growth(
        DashboardMetricsService.get_monthly_revenue,
        start_date, end_date,
        timedelta(days=(end_date - start_date).days + 1)
    )
    attendance_growth = calculate_growth(
        DashboardMetricsService.get_attendance_rate,
        start_date, end_date,
        timedelta(days=(end_date - start_date).days + 1)
    )

    print("Metrics:", metrics)
    context = {
        "members": metrics["active_members"],  # e.g., 1248
        "revenue": metrics["monthly_revenue"], # e.g., 3420000
        "attendance": metrics["attendance_rate"], # e.g., 0.72 for 72%
        "members_growth": members_growth / 100,       # 0.12 for 12%
        "revenue_growth": revenue_growth / 100,       # 0.08 for 8%
        "attendance_growth": attendance_growth / 100 # -0.02 for -2%
    }

    return render(
        request,
        "partials/dashboard_key_metrics.html",
        context
    )

def dashboard_recent_activity(request):
    tenant = request.user.tenant  # current tenant instance
    with tenant_context(tenant):
        activities = ActivityService.get_recent_activities(limit=5)
    return render(
        request,
        "partials/dashboard_recent_activity.html",
        {"activities": activities}
    )

def member_list_partial(request):
    filter_type = request.GET.get("filter", "all")
    today = date.today()

    if filter_type == "active":
        members = Member.objects.filter(payments__expiration_date__gte=today).distinct()
    elif filter_type == "expired":
        members = Member.objects.filter(payments__expiration_date__lt=today).distinct()
    elif filter_type == "overdue":
        # Example: expired by more than 7 days
        members = Member.objects.filter(payments__expiration_date__lt=today).distinct()
    else:
        members = Member.objects.all()

    return render(request, "partials/member_rows.html", {"members": members, "today": today})


class MemberEditView(LoginRequiredMixin, UpdateView):
    model = Member
    form_class = NewMemberForm
    template_name = "dashboard/members/edit_member.html"
    success_url = reverse_lazy("members_list")
    context_object_name = "member"

    @transaction.atomic
    def form_valid(self, form):
        member = form.save()

        Activity.objects.create(
            user=self.request.user,
            activity_type=Activity.ActivityType.MEMBER_UPDATED,
            description=f"Member {member.name} was updated",
            metadata={
                "member_id": str(member.id),
                "member_name": member.name,
                "member_type": member.member_type,
            }
        )

        return super().form_valid(form)

class MemberList(LoginRequiredMixin, ListView):
    model = Member
    template_name = 'dashboard/members_list.html'
    context_object_name = 'members'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('payments')

        for member in queryset:
            latest_payment = member.payments.order_by('-expiration_date').first()
            if latest_payment:
                member.expiration_date = latest_payment.expiration_date
                member.days_left = (latest_payment.expiration_date - date.today()).days
            else:
                member.expiration_date = None
                member.days_left = None
        return queryset


class NewMemberView(LoginRequiredMixin, FormView):
    template_name = "dashboard/members/add_members.html"
    form_class = NewMemberForm
    success_url = reverse_lazy("members_list")

    @transaction.atomic
    def form_valid(self, form):
        today = timezone.now().date()

        member = form.save()

        if member.member_type == "one-time":
            expiration = today
        else:
            expiration = today + timedelta(days=30)

        MemberPayment.objects.create(
            member=member,
            amount=form.cleaned_data["amount"],
            date_of_payment=today,
            expiration_date=expiration,
            is_renewal=False,
        )

         # Activity: member created
        Activity.objects.create(
            user=self.request.user,
            activity_type=Activity.ActivityType.MEMBER_CREATED,
            description=f"Member {member.name} was created",
            metadata={
                "member_id": str(member.id),
                "member_name": member.name,
                "member_type": member.member_type,
            }
        )

        # Activity: payment successful
        Activity.objects.create(
            user=self.request.user,
            activity_type=Activity.ActivityType.PAYMENT_SUCCESS,
            description=f"Payment received for {member.name}",
            metadata={
                "member_id": str(member.id),
                "amount": float(form.cleaned_data["amount"]),
                "expiration_date": expiration.isoformat(),
            }
        )

        return super().form_valid(form)    


class ReportsDataView(View):
    def get(self, request, *args, **kwargs):

        current_time = timezone.now()

        renewals_by_month = (
            MemberPayment.objects.filter(is_renewal=True)
            .annotate(month=TruncMonth("date_of_payment"))
            .values("month")
            .annotate(count=Count("id"))
        )

        new_signups_by_month = (
            Member.objects
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
        )

        # 2. Membership Duration (months between first and last payment per member)
        duration_qs = (
            MemberPayment.objects
            .values("member_id")
            .annotate(
                start_date=Min("date_of_payment"),
                end_date=Max("expiration_date")
            )
            .annotate(
                duration=ExpressionWrapper(
                    F("end_date") - F("start_date"),
                    output_field=DurationField()
                )
            )
        )

        duration_data = [
            {"member_id": d["member_id"], "months": d["duration"].days // 30}
            for d in duration_qs if d["duration"]
        ]

        monthly_revenue = (
            MemberPayment.objects
            .annotate(month=TruncMonth("date_of_payment"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        return render(request, "dashboard/reports.html", {
            "renewals_by_month": list(renewals_by_month),
            "new_signups_by_month": list(new_signups_by_month),
            "membership_duration": duration_data,
            "monthly_revenue": list(monthly_revenue),
        })
    

class BrandSettingsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/brand_setting.html"


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/profile_setting.html"