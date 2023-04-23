from fastapi import FastAPI, Request
import telegram

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
