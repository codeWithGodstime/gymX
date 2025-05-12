from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class GymDashboardOveriew(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/gym_dashboard_overview.html'

class MemberList(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/members_list.html'