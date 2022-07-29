import json

import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from .models import CustomerSubscription, Product
from .stripe_utils.api import (
    create_stripe_customer,
    create_stripe_payment_card_method,
    create_stripe_price,
    create_stripe_product,
    create_stripe_subscription,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="Test Product")
        context = super(ProductLandingPageView, self).get_context_data(
            **kwargs
        )
        context.update(
            {
                "product": product,
                "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            }
        )
        return context


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event["type"] == "customer.subscription.created":
        subscription = event["data"]["object"]
        CustomerSubscription.objects.create(
            subscription_id=subscription["id"],
            customer_id=subscription["customer"],
        )

    return HttpResponse(status=200)


class StripeCustomerSubscriptionView(View):
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            stripe_payment_method = create_stripe_payment_card_method(
                number="4242424242424242",
                exp_month=6,
                exp_year=2023,
                cvc="314",
            )
            customer = create_stripe_customer(
                email=req_json["email"],
                stripe_payment_method_id=stripe_payment_method["id"],
            )
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            stripe_product = create_stripe_product(product_name=product.name)
            stripe_price = create_stripe_price(
                product_price=product.price,
                stripe_product_id=stripe_product["id"],
            )
            stripe_subscription = create_stripe_subscription(
                customer_id=customer["id"], stripe_price_id=stripe_price.id
            )
            return JsonResponse({"subscription_id": stripe_subscription.id})
        except Exception as e:
            return JsonResponse({"error": str(e)})
