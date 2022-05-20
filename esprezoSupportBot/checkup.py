import logging
import sys
from telegram import Update, Bot, ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CallbackContext, ConversationHandler, JobQueue, Job

import validators
import googlesheets
from datetime import time, datetime
import pytz


from config import BOT_API_KEY

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

service = googlesheets.sheetautorize()

PERIOD, DAY, TZONE, TIME = range(4)
NUM, MOOD, NOTES, DATE  = range(4)
MENU = "menu"

WEEK_DAYS = {
	"Понедельник": "monday",
	"Вторник": "tuesday",
	"Среда": "wednesday",
	"Четверг": "thursday",
	"Пятница": "friday",
	"Суббота": "saturday",
	"Воскресенье":"sunday",
}

WEEK_DAYS_N = {
	"Понедельник": 0,
	"Вторник": 1,
	"Среда": 2,
	"Четверг": 3,
	"Пятница": 4,
	"Суббота": 5,
	"Воскресенье": 6,
}

CHECKUP_MOOD = {
	"mood_01": "Страх",
	"mood_02": "Одиночество",
	"mood_03": "Грусть",
	"mood_04": "Обида",
	"mood_05": "Любовь",
	"mood_06": "Интерес",
	"mood_07": "Уверенность",
	"mood_08": "Счастье",
	"mood_09": "Спокойствие",
	"mood_10": "Злость",
	"mood_11": "Радость",
	"mood_12": "Тревога",
	"mood_13": "Гордость",
	"mood_14": "Скука",
}

def get_mood_inline_keyboard(n):
	inline_keyboard = [
				[
					InlineKeyboardButton("Страх", callback_data = "mood_01"),
					InlineKeyboardButton("Одиночество", callback_data = "mood_02")
				],
				[
					InlineKeyboardButton("Грусть", callback_data = "mood_03"),
					InlineKeyboardButton("Обида", callback_data = "mood_04")
				],
				[
					InlineKeyboardButton("Любовь", callback_data = "mood_05"),
					InlineKeyboardButton("Интерес", callback_data = "mood_06")
				],
				[
					InlineKeyboardButton("Уверенность", callback_data = "mood_07"),
					InlineKeyboardButton("Счастье", callback_data = "mood_08")
				],
				[
					InlineKeyboardButton("Спокойствие", callback_data = "mood_09"),
					InlineKeyboardButton("Злость", callback_data = "mood_10")
				],
				[
					InlineKeyboardButton("Радость", callback_data = "mood_11"),
					InlineKeyboardButton("Тревога", callback_data = "mood_12")
				],
				[
					InlineKeyboardButton("Гордость", callback_data = "mood_13"),
					InlineKeyboardButton("Скука", callback_data = "mood_14")
				],
				[InlineKeyboardButton("Изменить ответ", callback_data = f"checkup_{str(int(n) + 1)}")],
				[InlineKeyboardButton("Сохранить", callback_data = "Сохранить")],
				[InlineKeyboardButton("Другое", callback_data = "Другое")],
			]
	return (InlineKeyboardMarkup(inline_keyboard))

def get_timezone_inline_keyboard():
	inline_keyboard = [
		[InlineKeyboardButton("Калининград(МСК-1)", callback_data = "-01:00")],
		[InlineKeyboardButton("Москва (МСК)", callback_data = "+00:00")],
		[InlineKeyboardButton("Самара (МСК+1)", callback_data = "+01:00")],
		[InlineKeyboardButton("Екатеринбург (МСК+2)", callback_data = "+02:00")],
		[InlineKeyboardButton("Омск (МСК+3)", callback_data = "+03:00")],
		[InlineKeyboardButton("Красноярск (МСК+4)", callback_data = "+04:00")],
		[InlineKeyboardButton("Иркутск (МСК+5)", callback_data = "+05:00")],
		[InlineKeyboardButton("Якутск (МСК+6)", callback_data = "+06:00")],
		[InlineKeyboardButton("Владивосток (МСК+7)", callback_data = "+07:00")],
		[InlineKeyboardButton("Магадан (МСК+8)", callback_data = "+08:00")],
		[InlineKeyboardButton("Камчатка (МСК+9)", callback_data = "+09:00")]
	]
	return (InlineKeyboardMarkup(inline_keyboard))

def begin_checkup(context: CallbackContext):
	print(context.job.context)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton("1", callback_data = "checkup_0"),
					InlineKeyboardButton("2", callback_data = "checkup_1"),
					InlineKeyboardButton("3", callback_data = "checkup_2"),
					InlineKeyboardButton("4", callback_data = "checkup_3"),
					InlineKeyboardButton("5", callback_data = "checkup_4")
				],
				[
					InlineKeyboardButton("6", callback_data = "checkup_5"),
					InlineKeyboardButton("7", callback_data = "checkup_6"),
					InlineKeyboardButton("8", callback_data = "checkup_7"),
					InlineKeyboardButton("9", callback_data = "checkup_8"),
					InlineKeyboardButton("10", callback_data = "checkup_9")
				],
			]
			)
	context.bot.send_message(chat_id = int(context.job.context), text = f'Салют, {googlesheets.get_name_by_id(context.job.context)}!\n\nПришло время отследить своё состояние.\n\nОцени своё состояние от 1 до 10, где\n\n1 — «Ужасно, лучше бы этот день не начинался», а\n10 — «Я супер, готов(а) свернуть горы»', reply_markup = reply_markup)

def set_schedule(update: Update, context: CallbackContext, j):
	data = context.user_data
	cu_time = data[TIME].split(':')
	cu_tzone = data[TZONE].split(':')
	cu_time[0] = int(cu_time[0]) - int(cu_tzone[0])
	chat_id = update.message.chat_id
	current_jobs = j.get_jobs_by_name(str(chat_id))
	logger.info('data: %s', current_jobs)
	for job in current_jobs:
		job.schedule_removal()
	if data[DAY] == "Каждый день":
		j.run_daily(begin_checkup, context = chat_id, days=(0, 1, 2, 3, 4, 5, 6), time = time(hour=int(cu_time[0]), minute=int(cu_time[1]), second=00).replace(tzinfo=pytz.timezone("Europe/Moscow")), name=str(chat_id))
	else:
		j.run_daily(begin_checkup, context = chat_id, days=(WEEK_DAYS_N[data[DAY]], ), time = time(hour=int(cu_time[0]), minute=int(cu_time[1]), second=00).replace(tzinfo=pytz.timezone("Europe/Moscow")), name=str(chat_id))


def	checkup_time_handler(update: Update, context: CallbackContext):
	j = context.job_queue
	#print(j.jobs)
	time = validators.time_validator(text = update.message.text)
	if (time == -1):
		update.message.reply_text('Кажется, время задано неверно. Попробуй ещё!')
		return (TIME)
	context.user_data[TIME] = time
	logger.info('checkup data: %s', context.user_data)
	set_schedule(update, context, j)
	#print(j.jobs)
	googlesheets.checkup_register(update.message.from_user.id, context.user_data)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
		[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
	])
	update.message.reply_text("Супер! Вернёмся к тебе в это время", reply_markup = reply_markup)
	context.user_data.clear()
	return ConversationHandler.END

def other_mood(update: Update, context: CallbackContext):
	message =  update.message.text
	context.user_data[MOOD].append(message)
	logger.info('user_data: %s', context.user_data)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton("Хочу", callback_data = "Хочу"),
					InlineKeyboardButton("Не сегодня", callback_data = "Не сегодня")
				],])
	update.message.reply_text(f'{googlesheets.get_name_by_id(update.message.from_user.id)}, хочешь поделиться заметками о своём состоянии?', reply_markup = reply_markup)
	return ConversationHandler.END

def handle_notes(update: Update, context: CallbackContext):
	message =  update.message.text
	context.user_data[NOTES] = message
	now = datetime.now()
	context.user_data[DATE] = now.strftime("%Y/%m/%d")
	logger.info('user_data: %s', context.user_data)
	googlesheets.save_checkup_data(context.user_data, update.message.from_user.id)
	update.message.reply_text('Спасибо! Все твои записи хранятся в <b>Дневнике</b>📆', parse_mode = ParseMode.HTML)
	return ConversationHandler.END
