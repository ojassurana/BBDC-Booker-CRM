# Publishable = "pk_live_51KrCOaLTObQHYLJ1khpxHGm3tDncVAHicCiFtbTz7YPmz9az2teckmj6yiq07NYNk71UX7siUgOM4iMpwBjkBaX200pPxKFn0H"
# Secret = "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"

import stripe


stripe.api_key = "sk_test_51KrCOaLTObQHYLJ1PmfqCSsYuDxmqDV9sqTEaxNF0dLh7YZqBrA1J49rR7NnZnd7xIeRGPqmkuiuSqXFpDdYLUlY00bilidgOR"
user_id = "1234"

link = stripe.PaymentLink.create(
  line_items=[
    {
      "price": "price_1MyDlwLTObQHYLJ1TeBWclHj",
      "quantity": 1,
      "adjustable_quantity": {
        "enabled": True,
        "maximum": 30,
        "minimum": 1,
      },
    },
  ],
)

print(link)
