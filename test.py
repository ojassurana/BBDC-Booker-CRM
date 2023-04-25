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
