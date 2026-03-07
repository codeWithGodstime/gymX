from .models import Activity, MemberPayment, Members

class GymService:
    @staticmethod
    def get_dashboard_overview_data(gym):
        # Placeholder for actual data retrieval logic
        return {
            "total_members": 150,
            "active_members": 120,
            "monthly_revenue": 5000,
            "current_month": "September",
            "current_year": 2023,
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