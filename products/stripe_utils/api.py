import stripe


def create_stripe_payment_card_method(number, exp_month, exp_year, cvc):
    stripe_payment_method = stripe.PaymentMethod.create(
        type="card",
        card={
            "number": number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
        },
    )
    return stripe_payment_method


def create_stripe_customer(email, stripe_payment_method_id):
    customer = stripe.Customer.create(
        email=email,
        payment_method=stripe_payment_method_id,
        invoice_settings={"default_payment_method": stripe_payment_method_id},
    )
    return customer


def create_stripe_product(product_name):
    product = stripe.Product.create(name=product_name)
    return product
