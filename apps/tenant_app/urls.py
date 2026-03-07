from django.urls import path
from . import views

urlpatterns = [
    path('accounts/dashboard/', views.GymDashboardOveriew.as_view(), name='dashboard_overview'),
    path('dashboard/analytics/', views.dashboard_analytics, name='dashboard_analytics'),
    path('dashboard/members/', views.MemberList.as_view(), name='members_list'),
    path('dashboard/members/add/', views.NewMemberView.as_view(), name='members_add'),
    path("dashboard/reports/", views.ReportsDataView.as_view(), name="reports_data"),
]