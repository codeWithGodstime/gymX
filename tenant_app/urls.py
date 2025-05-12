from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.GymDashboardOveriew.as_view(), name='home'),
    path('dashboard/members/', views.MemberList.as_view(), name='members_list'),
]