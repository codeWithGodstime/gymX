from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.GymDashboardOveriew.as_view(), name='home'),
    path('dashboard/members/', views.MemberList.as_view(), name='members_list'),
    path('dashboard/members/add/', views.NewMemberView.as_view(), name='members_add'),
    path("dashboard/reports/", views.ReportsDataView.as_view(), name="reports_data"),
]