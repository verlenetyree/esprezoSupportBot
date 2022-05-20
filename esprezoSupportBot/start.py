import logging
import sys
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler

import validators
import googlesheets
import menu


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


UID, NAME, MAIL = range(3)

def start(update: Update, context: CallbackContext) -> NAME:
	uid =  update.message.from_user.id
	if googlesheets.check_id_duplication(uid) == 0:
		update.message.reply_text('Ты уже зарегестрирован(а)! ☺')
		return ConversationHandler.END
	update.message.reply_text('Как ты хочешь, чтобы бот обращался к тебе? Введи имя или прозвище:')
	context.user_data[UID] = uid
	return (NAME)

## -- РЕГЕСТРАЦИЯ --
def name_handler(update: Update, context: CallbackContext) -> MAIL:
	# получить имя
	context.user_data[NAME] = update.message.text
	logger.info('user_data: %s', context.user_data)

	# спросить почту
	update.message.reply_text('А теперь введи корпоративную почту, чтобы мы знали, кто ты 🙃')
	return (MAIL)


def mail_handler(update: Update, context: CallbackContext):
	# получить почту
	mail = validators.mail_validator(text = update.message.text)
	if mail == -1:
		update.message.reply_text('Упс, кажется, это не корпоративный e-mail esprezo. Проверь, всё ли верно?')
		return (MAIL)
	if googlesheets.check_mail_duplication(update.message.text) == 0:
		update.message.reply_text('Этот почтовый адрес уже зарегистрирован!\nЕсли это твой e-mail, и ты ещё не проходил(а) регистрацию, пожалуйста, напиши @vlatskaya. Она со всем разберётся. 💪')
		return (MAIL)
	context.user_data[MAIL] = update.message.text
	logger.info('user_data: %s', context.user_data)
	googlesheets.start_register(context.user_data)
	update.message.reply_text('Супер! Поехали вводить заботу о себе в привычку! 🚀')
	update.message.reply_text(menu.MENU_TEXT ,parse_mode = ParseMode.HTML, reply_markup = menu.get_menu_inline_keyboard())
	context.user_data.clear()
	return ConversationHandler.END
