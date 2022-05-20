from telegram import Update, Bot
from telegram.ext import CallbackContext, ConversationHandler

import googlesheets
from config import BOT_API_KEY


SENDER, USERNAME, TEXT = range(3)

def send_report(update: Update, context: CallbackContext):
	context.user_data[TEXT] = update.message.text
	message = f"СООБЩЕНИЕ ОБ ОШИБКЕ\nот: {context.user_data[SENDER]} (@{context.user_data[USERNAME]})\n\n{context.user_data[TEXT]}"
	Bot(token = BOT_API_KEY).send_message(chat_id = 264155711, text = message)
	update.message.reply_text("Твоё сообщение отправлено!")
	return ConversationHandler.END


def report(update: Update, context: CallbackContext):
	context.user_data[SENDER] = googlesheets.get_user_name(update.message.from_user.id)
	context.user_data[USERNAME] = update.message.from_user.username
	update.message.reply_text('Расскажи о проблеме, с которой ты столкнулся❣')
	return (TEXT)
