from django.urls import path
from .views import LandingPageView
from django.views.generic import TemplateView


urlpatterns = [
    path("", LandingPageView.as_view()),
    path("pricing", TemplateView.as_view(template_name="pricing.html"), name="pricing"),
]