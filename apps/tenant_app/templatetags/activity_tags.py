from django import template
from apps.tenant_app.models import Activity

register = template.Library()

# Map activity types to icons
ICONS = {
    Activity.ActivityType.MEMBER_CREATED: "person_add",
    Activity.ActivityType.MEMBER_UPDATED: "edit",
    Activity.ActivityType.MEMBER_DELETED: "person_remove",
    Activity.ActivityType.MEMBER_CHECKIN: "check_circle",
    Activity.ActivityType.PAYMENT_SUCCESS: "payments",
    Activity.ActivityType.PAYMENT_FAILED: "warning",
    Activity.ActivityType.PLAN_CREATED: "add_chart",
    Activity.ActivityType.PLAN_UPDATED: "update",
    Activity.ActivityType.STAFF_ADDED: "badge",
}

# Map activity types to bg colors
BG_CLASSES = {
    Activity.ActivityType.MEMBER_CREATED: "bg-primary/10",
    Activity.ActivityType.MEMBER_UPDATED: "bg-blue-100 dark:bg-blue-900/30",
    Activity.ActivityType.MEMBER_DELETED: "bg-rose-100 dark:bg-rose-900/30",
    Activity.ActivityType.MEMBER_CHECKIN: "bg-emerald-100 dark:bg-emerald-900/30",
    Activity.ActivityType.PAYMENT_SUCCESS: "bg-emerald-100 dark:bg-emerald-900/30",
    Activity.ActivityType.PAYMENT_FAILED: "bg-rose-100 dark:bg-rose-900/30",
    Activity.ActivityType.PLAN_CREATED: "bg-indigo-100 dark:bg-indigo-900/30",
    Activity.ActivityType.PLAN_UPDATED: "bg-yellow-100 dark:bg-yellow-900/30",
    Activity.ActivityType.STAFF_ADDED: "bg-purple-100 dark:bg-purple-900/30",
}

# Map activity types to text/icon color
TEXT_CLASSES = {
    Activity.ActivityType.MEMBER_CREATED: "text-primary",
    Activity.ActivityType.MEMBER_UPDATED: "text-blue-600",
    Activity.ActivityType.MEMBER_DELETED: "text-rose-600",
    Activity.ActivityType.MEMBER_CHECKIN: "text-emerald-600",
    Activity.ActivityType.PAYMENT_SUCCESS: "text-emerald-600",
    Activity.ActivityType.PAYMENT_FAILED: "text-rose-600",
    Activity.ActivityType.PLAN_CREATED: "text-indigo-600",
    Activity.ActivityType.PLAN_UPDATED: "text-yellow-600",
    Activity.ActivityType.STAFF_ADDED: "text-purple-600",
}

DESCRIPTIONS = {
    Activity.ActivityType.MEMBER_CREATED: "joined the gym",
    Activity.ActivityType.MEMBER_UPDATED: "was updated",
    Activity.ActivityType.MEMBER_DELETED: "was removed",
    Activity.ActivityType.MEMBER_CHECKIN: "checked in",
    Activity.ActivityType.PAYMENT_SUCCESS: "payment successful",
    Activity.ActivityType.PAYMENT_FAILED: "payment failed",
    Activity.ActivityType.PLAN_CREATED: "created a plan",
    Activity.ActivityType.PLAN_UPDATED: "updated a plan",
    Activity.ActivityType.STAFF_ADDED: "added staff",
}

@register.filter
def activity_icon(activity_type):
    return ICONS.get(activity_type, "info")

@register.filter
def activity_type_bg(activity_type):
    return BG_CLASSES.get(activity_type, "bg-slate-100")

@register.filter
def activity_type_text(activity_type):
    return TEXT_CLASSES.get(activity_type, "text-slate-700")

@register.filter
def activity_description(activity):
    """
    Returns a human-readable description for the activity, including optional metadata.
    """
    desc = DESCRIPTIONS.get(activity.activity_type, "did something")
    # You can add plan name, amount, or other metadata if needed
    if activity.activity_type in [Activity.ActivityType.PAYMENT_SUCCESS, Activity.ActivityType.PAYMENT_FAILED]:
        amount = activity.metadata.get("amount") if activity.metadata else None
        if amount:
            desc += f" • {amount}"
    elif activity.activity_type in [Activity.ActivityType.MEMBER_CHECKIN]:
        plan = activity.metadata.get("plan_name") if activity.metadata else None
        if plan:
            desc += f" • {plan}"
    return desc