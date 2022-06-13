from django.contrib import admin
from django.urls import path
from products.views import (
    ProductLandingPageView,
    stripe_webhook,
    StripeCustomerSubscriptionView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('', ProductLandingPageView.as_view(), name='landing-page'),
    path('subscription/<pk>/', StripeCustomerSubscriptionView.as_view(), name='stripe-subscription'),
]
