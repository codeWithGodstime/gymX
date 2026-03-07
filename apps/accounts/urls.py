from django.urls import path, include
from .views import (
    GymOwnerSignupWizard, 
    SubscriptionView, 
    InitializePaymentView, 
    PaymentCallbackView,
    TenantLoginView,
    TenantLogoutView
)

urlpatterns = [
    path("accounts/logout/", TenantLogoutView.as_view(), name='accounts_logout'),
    path("accounts/login/", TenantLoginView.as_view(), name='accounts_login'),
    path("accounts/signup/", GymOwnerSignupWizard.as_view(), name='accounts_signup'),
    path("accounts/subscription/", SubscriptionView.as_view(), name='subscription'),
    path("accounts/payment/initialize/", InitializePaymentView.as_view(), name='initialize_payment'),
    path("accounts/payment/callback/", PaymentCallbackView.as_view(), name='payment_callback'),
    path("accounts/", include("allauth.urls")),
]