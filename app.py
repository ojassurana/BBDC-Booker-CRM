from fastapi import FastAPI, Request
import telegram
import json
import stripe


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
async def echo(request: Request):
    update_data = await request.json()
    print(update_data)
    return {"status": "ok"}
