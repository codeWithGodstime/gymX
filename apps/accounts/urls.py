from django.urls import path, include
from .views import (
    GymOwnerSignupView, 
    SubscriptionView, 
    InitializePaymentView, 
    PaymentCallbackView,
    TenantLoginView,
    TenantLogoutView
)

urlpatterns = [
    path("accounts/logout/", TenantLogoutView.as_view(), name='logout'),
    path("accounts/login/", TenantLoginView.as_view(), name='login'),
    path("accounts/signup/", GymOwnerSignupView.as_view()),
    path("accounts/subscription/", SubscriptionView.as_view(), name='subscription'),
    path("accounts/payment/initialize/", InitializePaymentView.as_view(), name='initialize_payment'),
    path("accounts/payment/callback/", PaymentCallbackView.as_view(), name='payment_callback'),
    path("accounts/", include("allauth.urls")),
]