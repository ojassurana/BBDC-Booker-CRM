import stripe

stripe.api_key = "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"

def get_payment_id(checkout_id):
    session = stripe.checkout.Session.retrieve(checkout_id)
    payment_intent_id = session.payment_intent
    print(session)
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    return payment_intent.id

# Example usage
checkout_id = "cs_live_a173MbvXxNIi2qNcPEmZvR6r8hDVESdvKHpeCjQMNmC2Kg1KdF7033xo2h"
payment_id = get_payment_id(checkout_id)
print(payment_id)
