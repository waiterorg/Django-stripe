import json
import stripe
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views import View
from .models import CustomerSubscription, Product


stripe.api_key = settings.STRIPE_SECRET_KEY

class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="Test Product")
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
        })
        return context


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
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
         subscription = event['data']['object']
         CustomerSubscription.objects.create(subscription_id=subscription['id'], customer_id=subscription['customer'])
         
    return HttpResponse(status=200)


class StripeCustomerSubscriptionView(View):    
    def post(self, request, *args, **kwargs):
        try:
            req_json = json.loads(request.body)
            stripe_payment_method = stripe.PaymentMethod.create(
              type="card",
              card={
                "number": "4242424242424242",
                "exp_month": 6,
                "exp_year": 2023,
                "cvc": "314",
              },
            )
            customer = stripe.Customer.create(
              email=req_json['email'],
              payment_method=stripe_payment_method['id'],
              invoice_settings={
                  'default_payment_method' : stripe_payment_method['id']
              },
            )
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            stripe_product = stripe.Product.create(name=product.name)
            stripe_price = stripe.Price.create(
                unit_amount=product.price,
                currency="usd",
                recurring={"interval": "month"},
                product=stripe_product['id'],
            )
            
            stripe_subscription = stripe.Subscription.create(
                customer=customer['id'],
                items=[
                  {"price": stripe_price.id},
                ],
                payment_behavior="allow_incomplete"
            )
            return JsonResponse({
                'subscription_id': stripe_subscription.id
            })
        except Exception as e:
            return JsonResponse({ 'error': str(e) })
