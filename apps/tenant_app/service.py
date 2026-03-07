from .models import Activity, MemberPayment, Members, Attendance
from django.db.models import Sum, Count
from datetime import date


class DashboardMetricsService:
    @staticmethod
    def get_active_members_count(start_date=None, end_date=None):
        """
        Count members whose payment is currently active (not expired) within optional date range.
        """
        qs = Members.objects.filter(
            member_payments__expiration_date__gte=date.today()
        ).distinct()

        if start_date:
            qs = qs.filter(member_payments__date_of_payment__gte=start_date)
        if end_date:
            qs = qs.filter(member_payments__date_of_payment__lte=end_date)
        
        return qs.count()

    @staticmethod
    def get_monthly_revenue(start_date=None, end_date=None):
        """
        Sum of payments within optional date range
        """
        qs = MemberPayment.objects.all()
        if start_date:
            qs = qs.filter(date_of_payment__gte=start_date)
        if end_date:
            qs = qs.filter(date_of_payment__lte=end_date)
        
        revenue = qs.aggregate(total=Sum("amount"))["total"] or 0
        return revenue

    @staticmethod
    def get_attendance_rate(start_date=None, end_date=None):
        """
        Placeholder: Returns 0 if you don't yet track attendance.
        Replace with real Attendance model if available.
        """
        # If you have an Attendance model, filter by start_date/end_date
        return 0

    @classmethod
    def get_dashboard_metrics(cls, start_date=None, end_date=None):
        return {
            "active_members": cls.get_active_members_count(start_date, end_date),
            "monthly_revenue": cls.get_monthly_revenue(start_date, end_date),
            "attendance_rate": cls.get_attendance_rate(start_date, end_date),
        }    

class ActivityService:
    """
    Handles creation and retrieval of activity logs
    """

    # ---------------------------
    # Member Activities
    # ---------------------------

    @staticmethod
    def member_created(member, user=None):
        Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.MEMBER_CREATED,
            description=f"{member.full_name} was added as a member",
            metadata={
                "member_id": member.id,
            },
        )

    @staticmethod
    def member_updated(member, user=None):
        Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.MEMBER_UPDATED,
            description=f"{member.full_name}'s details were updated",
            metadata={
                "member_id": member.id,
            },
        )

    @staticmethod
    def member_deleted(member_name, member_id=None, user=None):
        Activity.objects.create(
            user=user,
            activity_type=Activity.ActivityType.MEMBER_DELETED,
            description=f"{member_name} was removed from members",
            metadata={
                "member_id": member_id,
            },
        )

    # ---------------------------
    # Queries
    # ---------------------------
    @staticmethod
    def get_recent_activities(limit=6):
        """
        Returns the latest `limit` activities for the tenant.
        """
        return (
            Activity.objects
            .select_related("user")
            .order_by("-created_at")[:limit]
        )

    @staticmethod
    def get_all_activities(tenant):
        """
        Returns all activities for the tenant.
        """
        return Activity.objects.filter(tenant=tenant).select_related("user").order_by("-created_at")