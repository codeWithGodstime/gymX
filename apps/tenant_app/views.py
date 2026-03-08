from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse_lazy
from datetime import date, timedelta
from django.views.generic import TemplateView, ListView, FormView, View
from django.views.generic.edit import UpdateView
from django_tenants.utils import tenant_context

from django.db.models import F, ExpressionWrapper, Count, Sum, DurationField, Min, Max
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.mixins import LoginRequiredMixin
from .service import DashboardMetricsService, ActivityService

from .forms import NewMemberForm
from .models import Member, MemberPayment, Activity
from apps.utils import SubscriptionRequiredMixin



class GymDashboardOveriew(SubscriptionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/gym_dashboard_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context


class DashboardAnalyticsView(SubscriptionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "partials/dashboard_key_metrics.html"

    def get_filter_dates(self):
        filter_type = self.request.GET.get("filter", "month")
        today = date.today()

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

        return start_date, end_date

    def calculate_growth(self, metric_fn, start, end):
        period_delta = timedelta(days=(end - start).days + 1)
        prev_start = start - period_delta
        prev_end = end - period_delta
        current = metric_fn(start, end)
        previous = metric_fn(prev_start, prev_end)
        if previous == 0:
            return 0
        return round(((current - previous) / previous) * 100, 1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = self.get_filter_dates()

        metrics = DashboardMetricsService.get_dashboard_metrics(start_date, end_date)

        members_growth = self.calculate_growth(
            DashboardMetricsService.get_active_members_count,
            start_date, end_date
        )
        revenue_growth = self.calculate_growth(
            DashboardMetricsService.get_monthly_revenue,
            start_date, end_date
        )
        attendance_growth = self.calculate_growth(
            DashboardMetricsService.get_attendance_rate,
            start_date, end_date
        )

        context.update({
            "members": metrics["active_members"],
            "revenue": metrics["monthly_revenue"],
            "attendance": metrics["attendance_rate"],
            "members_growth": members_growth / 100,
            "revenue_growth": revenue_growth / 100,
            "attendance_growth": attendance_growth / 100
        })

        return context
    

class DashboardRecentActivityView(SubscriptionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "partials/dashboard_recent_activity.html"
    limit = 5  # default number of recent activities

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tenant = self.request.user.tenant  # current tenant instance

        with tenant_context(tenant):
            activities = ActivityService.get_recent_activities(limit=self.limit)

        context["activities"] = activities
        return context


class MemberListPartialView(SubscriptionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "partials/member_rows.html"

    def get_filter_type(self):
        return self.request.GET.get("filter", "all")

    def get_queryset(self):
        filter_type = self.get_filter_type()
        today = date.today()

        if filter_type == "active":
            return Member.objects.filter(payments__expiration_date__gte=today).distinct()
        elif filter_type == "expired":
            return Member.objects.filter(payments__expiration_date__lt=today).distinct()
        elif filter_type == "overdue":
            # Example: expired by more than 7 days
            return Member.objects.filter(payments__expiration_date__lt=today).distinct()
        else:
            return Member.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members"] = self.get_queryset()
        context["today"] = date.today()
        return context


class MemberEditView(SubscriptionRequiredMixin, LoginRequiredMixin, UpdateView):
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


class MemberList(SubscriptionRequiredMixin, LoginRequiredMixin, ListView):
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


class NewMemberView(SubscriptionRequiredMixin, LoginRequiredMixin, FormView):
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


class ReportsDataView(SubscriptionRequiredMixin, LoginRequiredMixin, View):
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
    

class BrandSettingsView(SubscriptionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "dashboard/brand_setting.html"


class SettingsView(SubscriptionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = "dashboard/profile_setting.html"