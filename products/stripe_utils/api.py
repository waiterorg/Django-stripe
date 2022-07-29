import stripe


def stripe_payment_card_method(number, exp_month, exp_year, cvc):
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
