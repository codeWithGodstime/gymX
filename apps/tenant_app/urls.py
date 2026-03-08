from django.urls import path
from . import views

urlpatterns = [
    path('accounts/overview/', views.GymDashboardOveriew.as_view(), name='dashboard_overview'),
    path('dashboard/analytics/', views.dashboard_analytics, name='dashboard_analytics'),
    path('dashboard/recent-activity/', views.dashboard_recent_activity, name='dashboard_recent_activity'),
    path("members/partial/", views.member_list_partial, name="member_list_partial"),
    path('dashboard/members/', views.MemberList.as_view(), name='members_list'),
    path('dashboard/members/add/', views.NewMemberView.as_view(), name='members_add'),
    path('dashboard/members/<str:pk>/edit/', views.MemberEditView.as_view(), name='member_edit'),
    path("accounts/settings/", views.SettingsView.as_view(), name="profile_settings"),
    path("accounts/settings/brand/", views.BrandSettingsView.as_view(), name="brand_settings"),
    path("dashboard/reports/", views.ReportsDataView.as_view(), name="reports_data"),
]