
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import googlesheets
from datetime import time, datetime
import sys
import logging

HELP, INDEX, TODAY = range(3)
MENU = "menu"

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

HELP_TEXT = '''Команда рядом и хочет поддержать тебя. Какая поддержка тебе ближе?

1. Больше разговоров: делиться новостями, мнениями, эмоциями

2. Инструменты, как справиться со сложными чувствами, эмоциональными качелями

3. Совместная физическая активность: Телозамес, зарядка утром, тренировки

4. Полезные лекции, МК, по навыкам которые нужны в новой реальности: финансы, планирование и тп.

5. Творчество: рисовать, читать, смотреть фильмы, решать головоломки и тп.

6. Трансформационная игра: Путь к мечте

7. Дыхательные практики

8. Личный чёткий план на ближайшее будущее

9. Отпуск бы или отгул

10. Больше благодарностей, разговоров про успехи

11. Брейнсторминги по помощи компании

12. Коворкинг или очные встречи'''

HELP_LIST = {
	1: 'Больше разговоров: делиться новостями, мнениями, эмоциями',

	2: 'Инструменты, как справиться со сложными чувствами, эмоциональными качелями',

	3: 'Совместная физическая активность: Телозамес, зарядка утром, тренировки',

	4: 'Полезные лекции, МК, по навыкам которые нужны в новой реальности: финансы, планирование и тп.',

	5: 'Творчество: рисовать, читать, смотреть фильмы, решать головоломки и тп.',

	6: 'Трансформационная игра: Путь к мечте',

	7: 'Дыхательные практики',

	8: 'Личный чёткий план на ближайшее будущее',

	9: 'Отпуск бы или отгул',

	10: 'Больше благодарностей, разговоров про успехи',

	11: 'Брейнсторминги по помощи компании',

	12: 'Коворкинг или очные встречи',
}

def other_help(update: Update, context: CallbackContext):
	message =  update.message.text
	context.user_data[HELP].append(message)
	context.user_data[INDEX].append("Другое")
	now = datetime.now()
	context.user_data[TODAY] = now.strftime("%Y/%m/%d")
	logger.info('user_data: %s', context.user_data)
	googlesheets.save_help_data(context.user_data, update.message.from_user.id)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
	update.message.reply_text(f'Спасибо, {googlesheets.get_name_by_id(update.message.from_user.id)}! Просить поддержки нормально, с тобой всё в порядке❤️', reply_markup = reply_markup)
	return ConversationHandler.END
