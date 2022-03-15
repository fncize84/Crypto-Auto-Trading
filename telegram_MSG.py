import telegram

token = "5094155373:AAGwbZOBTw990tvU6TIdHWilsHP7R95T-qM"
chat_id = "5033041863"

def post_message(message):
	bot = telegram.Bot(token)
	bot.sendMessage(chat_id=chat_id, text=message)
def post_photo(img):
	bot = telegram.Bot(token)
	bot.sendPhoto(chat_id, open(img,'rb'))