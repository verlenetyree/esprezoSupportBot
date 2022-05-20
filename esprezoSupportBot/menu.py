from telegram import Update, ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

CHECKUP_BUTTON = "Чекап 💌"
GRATITUDE_BUTTON = "Благодарность 🥰"
UTILITY_BUTTON = "Полезности 📚"
DIARY_BUTTON = "Дневник 📆"
HELP_BUTTON = "ПАМАГИТЕ ✊"
SETTINGS_BUTTON = "Настройки ⚙️"

MENU_TEXT = f'''Сейчас расскажем тебе, что можно сделать в каждом пункте главного меню 🌚

{CHECKUP_BUTTON} — ответить на три вопроса и зафиксировать своё состояние.

{GRATITUDE_BUTTON} — отправить письмо с благодарностями или поддержкой кому-то из команды.

{UTILITY_BUTTON} — изучить материалы и практики для самоподдержки.

{DIARY_BUTTON} — посмотреть свои чекапы за последнее время и отследить динамику состояния.

{HELP_BUTTON} — попросить поддержки или совет у кого-то из команды.

{SETTINGS_BUTTON} — поменять имя, время и частоту чекапа.'''


def get_menu_inline_keyboard():
	inline_keyboard = [
		[InlineKeyboardButton(CHECKUP_BUTTON, callback_data = "CHECKUP_BUTTON")],
		[InlineKeyboardButton(GRATITUDE_BUTTON, callback_data = "GRATITUDE_BUTTON")],
		[InlineKeyboardButton(UTILITY_BUTTON, callback_data = "UTILITY_BUTTON")],
		[InlineKeyboardButton(DIARY_BUTTON, callback_data = "DIARY_BUTTON")],
		[InlineKeyboardButton(HELP_BUTTON, callback_data = "HELP_BUTTON")],
		[InlineKeyboardButton(SETTINGS_BUTTON, callback_data = "SETTINGS_BUTTON")],
	]
	return (InlineKeyboardMarkup(inline_keyboard))

def menu(update: Update, context: CallbackContext):
	update.message.reply_text(MENU_TEXT, parse_mode = ParseMode.HTML, reply_markup = get_menu_inline_keyboard())

