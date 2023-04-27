from fastapi import FastAPI, Request
import telegram
import json
import stripe
from fastapi import FastAPI, Request, Header



stripe.api_key = "sk_test_51KrCOaLTObQHYLJ1PmfqCSsYuDxmqDV9sqTEaxNF0dLh7YZqBrA1J49rR7NnZnd7xIeRGPqmkuiuSqXFpDdYLUlY00bilidgOR"
TOKEN = '5641356025:AAFhotXRyhkUXWcFBXhSN78gs0Hk9AjPpNY'
bot = telegram.Bot(TOKEN)

app = FastAPI()


async def send_text(chat_id, message_text):
    await bot.send_message(chat_id, message_text)


@app.post("/")
async def echo(request: Request):
    update_data = await request.json()
    update = telegram.Update.de_json(update_data, bot)
    chat_id = update.message.chat.id
    message_text = update.message.text
    await send_text(chat_id, message_text)
    return {"status": "ok"}


@app.post("/form")
async def echo(request: Request):
    update_data = dict(await request.form())
    print(update_data)
    return {"status": "ok"}



@app.post("/stripe")
async def webhook_received(request: Request, stripe_signature: str = Header(None)):
    webhook_secret = "whsec_OdELm7jA3z4NfY8m1qY7ouTrYnO6XQ8F"
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=webhook_secret
        )
        event_data = event['data']
    except Exception as e:
        return {"error": str(e)}
    print(event)
    event_type = event['type']
    if event_type == 'checkout.session.completed':
        print('checkout session completed')
    elif event_type == 'invoice.paid':
        print('invoice paid')
    elif event_type == 'invoice.payment_failed':
        print('invoice payment failed')
    else:
        print(f'unhandled event: {event_type}')
    
    return {"status": "success"}


# https://5fb0-180-129-64-91.ngrok.ioq



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