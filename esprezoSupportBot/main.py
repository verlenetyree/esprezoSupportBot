import logging
import sys
import ast
from telegram import Bot, Update, ParseMode, Message
from telegram import  ReplyKeyboardMarkup, KeyboardButton
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler,Filters, JobQueue

from config import BOT_API_KEY
import validators, report
import googlesheets
import menu, start, checkup, utility, needhelp
import gratitude
from gratitude import TEAM_PERSONS
from checkup import CHECKUP_MOOD
import regex as re
from datetime import date, datetime, timedelta

from collections import Counter

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

UID, NAME, MAIL = range(3)
PERIOD, DAY, TZONE, TIME = range(4)
TO, FROM, MESSAGE = range(3)
NUM, MOOD, NOTES, DATE  = range(4)
SENDER, USERNAME, TEXT = range(3)
HELP, INDEX, TODAY, = range(3)

TEAM1 = "partners"
TEAM2 = "scenarists"
TEAM3 = "designers"
TEAM4 = "MPRs"
TEAM5 = "projects"
TEAM6 = "education"
TEAM7 = "hr"
TEAM8 = "marketing"
TEAM9 = "OMs"
TEAM10 = "МРАК"
DRAFTS = "drafts"
MENU = "menu"

PDAY = "Раз в день"
PWEEK = "Раз в неделю"

WEEK = {
	1: "Понедельник",
	2: "Вторник",
	3: "Среда",
	4: "Четверг",
	5: "Пятница",
	6: "Суббота",
	7: "Воскременье",
}

WEEK2 = {
	"Monday": "Понедельник",
	"Tuesday": "Вторник",
	"Wednesday": "Среда",
	"Thursday": "Четверг",
	"Friday": "Пятница",
	"Saturday": "Суббота",
	"Sunday": "Воскресенье",
}

def cancel_handler(update: Update, context: CallbackContext):
	# Отменить весь процесс диалога. Данные будут утеряны
	update.message.reply_text('Чтобы зарегестрировать снова нажми /start')
	return ConversationHandler.END

def makeplot(x, y):
	ax = plt.axes()
	ax.set_ylim(0, 11)
	ax.yaxis.set_ticks(range(1, 11))
	ax.tick_params(labelsize=10)
	ax.yaxis.grid(True, which='major', linewidth=0.5, color='lightgray')
	ax.xaxis.grid(True, which='major', linewidth=0.5, color='lightgray')
	ax.xaxis.set_ticks(x)
	ax.xaxis.set_ticklabels(x, rotation = -20)
	if (len(x) == 1):
		plt.plot(x, y, color='plum', marker='o')
	else:
		plt.plot(x, y, linewidth='4', color='plum')
	plt.title("Динамика твоего состояния")
	plt.savefig('img/checkup.png')
	plt.clf()


def	button_reply_handler(update: Update, context: CallbackContext):
	query = update.callback_query
	data = query.data
	# -----	ЧЕКАПЫ ----- #
	if (data == "CHECKUP_BUTTON"):
		check = googlesheets.check_if_registred(query.from_user.id)
		if (check != 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton("Да", callback_data = "checkup_yes"),
					InlineKeyboardButton("Нет", callback_data = MENU)
				],
			]
			)
			query.edit_message_text(f"<b>Твоё время чекапов:</b>\n\n<code>{check[1]} в {check[3]} ({check[2]})</code>\n\nХочешь получать уведомления в другое время?", parse_mode = ParseMode.HTML, reply_markup = reply_markup)
		else:
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton(PDAY, callback_data = PDAY),
					InlineKeyboardButton(PWEEK, callback_data = PWEEK)
				],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			]
			)
			query.edit_message_text("Как часто ты хочешь проходить чекапы?", reply_markup = reply_markup)

	elif (data == PDAY or data == PWEEK):
		context.user_data[PERIOD] = data
		if (data == PWEEK):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[InlineKeyboardButton(WEEK[1], callback_data = WEEK[1])],
				[InlineKeyboardButton(WEEK[2], callback_data = WEEK[2])],
				[InlineKeyboardButton(WEEK[3], callback_data = WEEK[3])],
				[InlineKeyboardButton(WEEK[4], callback_data = WEEK[4])],
				[InlineKeyboardButton(WEEK[5], callback_data = WEEK[5])],
				[InlineKeyboardButton(WEEK[6], callback_data = WEEK[6])],
				[InlineKeyboardButton(WEEK[7], callback_data = WEEK[7])]
		])
			query.edit_message_text("Хорошо, а теперь выбери подходящий день недели.", reply_markup = reply_markup)
		else:
			context.user_data[DAY] = "Каждый день"
			logger.info('checkup data: %s', context.user_data)
			query.edit_message_text("Выбери часовой пояс, чтобы мы присылали уведомления в удобное время.", reply_markup = checkup.get_timezone_inline_keyboard())

	elif (data == WEEK[1] or data == WEEK[2] or data == WEEK[3] or data == WEEK[4] or
		data == WEEK[5] or data == WEEK[6] or data == WEEK[7]):
		context.user_data[DAY] = data
		logger.info('checkup data: %s', context.user_data)
		query.edit_message_text("Выбери часовой пояс, чтобы мы присылали уведомления в удобное время.", reply_markup = checkup.get_timezone_inline_keyboard())

	elif (data == "-01:00" or data == "+00:00" or data == "+01:00" or data == "+02:00" or data == "+03:00" or data == "+04:00" or
		  data == "+05:00" or data == "+06:00" or data == "+07:00" or data == "+08:00" or data == "+09:00"):
		context.user_data[TZONE] = data
		query.edit_message_text("Введи время чекапа в 24-часовом формате (чч:мм). Например, 12:30 или 20:00.")
		return(TIME)

	elif (data == "checkup_yes"):
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton(PDAY, callback_data = PDAY),
					InlineKeyboardButton(PWEEK, callback_data = PWEEK)
				],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			]
			)
		query.edit_message_text("Как часто ты хочешь проходить чекапы?", reply_markup = reply_markup)

	elif (re.search("^checkup_[0-9]$", data)):
		context.user_data[NUM] = data.split('_')[1]
		context.user_data[MOOD] = []
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
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
				[InlineKeyboardButton("Другое", callback_data = "Другое")],
				[InlineKeyboardButton("Сохранить", callback_data = "Сохранить")],
			]
			)
		query.edit_message_text(f'Что ты сейчас чувствуешь (ты можешь выбрать несколько вариантов)\n\nНажми "<b>Сохранить</b>", чтобы записать ответ. Ты можешь дополнить ответ, выбрав "<b>Другое</b>."', reply_markup = reply_markup, parse_mode = ParseMode.HTML)

	elif (re.search("^mood_[0-9]{2}$", data)):
		context.user_data[MOOD].append(CHECKUP_MOOD[data])
		reply_markup = checkup.get_mood_inline_keyboard(context.user_data[NUM])
		query.edit_message_text(f'Что ты сейчас чувствуешь (ты можешь выбрать несколько вариантов)\n\nНажми "<b>Сохранить</b>", чтобы записать ответ. Ты можешь дополнить ответ, выбрав "<b>Другое</b>".\n\nТы выбрал(а): <i>{", ".join(context.user_data[MOOD])}</i>', reply_markup = reply_markup, parse_mode = ParseMode.HTML)

	elif (data == "Другое"):
		query.edit_message_text('Прислушайся к себе и напиши, что ты чувствуешь прямо сейчас.')
		return (MOOD)

	elif (data == "Сохранить"):
		if (context.user_data[MOOD] == []):
			reply_markup = checkup.get_mood_inline_keyboard(context.user_data[NUM])
			query.edit_message_text(f'Что ты сейчас чувствуешь (ты можешь выбрать несколько вариантов)\n\nНажми "<b>Сохранить</b>", чтобы записать ответ. Ты можешь дополнить ответ, выбрав "<b>Другое</b>".\n\nТы выбрал(а): <i>{", ".join(context.user_data[MOOD])}</i>', reply_markup = reply_markup, parse_mode = ParseMode.HTML)
		else:
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[
						InlineKeyboardButton("Хочу", callback_data = "Хочу"),
						InlineKeyboardButton("Не сегодня", callback_data = "Не сегодня")
					],])
			query.edit_message_text(f'{googlesheets.get_name_by_id(query.from_user.id)}, хочешь поделиться заметками о своём состоянии?', reply_markup = reply_markup)

	elif (data == "Хочу"):
		query.edit_message_text('Отлично! Эти записи будут в боте, и ты сможешь вернуться к ним в любой момент, чтобы порефлексировать. Можешь выписать поток мыслей или опереться на вопросы ниже.\n\nКакие ассоциации у тебя с этим состоянием? Скажем, если бы состояние было местом, предметом или человеком, то что бы или кто бы это был? Любые метафоры помогают шире видеть и чувствовать.\n\nЧто тебе хочется сказать самому себе и сделать из этого состояния? Как поддержать? Помочь? Поблагодарить? Утешить? Обнять?')
		return (NOTES)

	elif (data == "Не сегодня"):
		context.user_data[NOTES] = "null"
		now = datetime.now()
		context.user_data[DATE] = now.strftime("%Y/%m/%d")
		logger.info('checkup data: %s', context.user_data)
		googlesheets.save_checkup_data(context.user_data, query.from_user.id)
		query.edit_message_text("Хорошо! Рассказывай о себе, только если чувствуешь в этом потребность. Увидимся на следующем чекапе😉")

	# ----- БЛАГОДАРНОСТИ ----- #
	elif (data == "GRATITUDE_BUTTON"):
		query.edit_message_text("Мы рады, что у тебя есть ресурс поддержать команду💜\n\nВыбери, человеку из какой комнадочки ты хочешь написать письмо.",
								reply_markup = gratitude.get_gratitude_inline_keyboard())

	elif (data == DRAFTS):
		drafts = googlesheets.get_drafts(query.from_user.id)
		context.user_data[0] = drafts
		if (drafts == 0):
			query.edit_message_text("У тебя пока нет черновиков")
		else:
			count = len(drafts)
			if count > 1:
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[
						InlineKeyboardButton(f"К последнему", callback_data = f"draft_{count - 1}"),
						InlineKeyboardButton("2 ➡", callback_data = "draft_1")],
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
			else:
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
			query.edit_message_text(f"Кому: <code>{ast.literal_eval(drafts[0])[0]}</code>\n\n{ast.literal_eval(drafts[0])[2]}", parse_mode = ParseMode.HTML, reply_markup = reply_markup)

	elif (re.search("^draft_\d{1,}$", data)):
		drafts = context.user_data[0]
		count = len(drafts)
		num = int((re.search("\d{1,}", data)).group(0))
		if (num != count - 1 and num > 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton(f"{num} ⬅", callback_data = f"draft_{num - 1}"),
					InlineKeyboardButton(f"{num + 2} ➡", callback_data = f"draft_{num + 1}")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
		elif (num == 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton(f"К последнему", callback_data = f"draft_{count - 1}"),
					InlineKeyboardButton("2 ➡", callback_data = "draft_1")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
		else:
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[InlineKeyboardButton(f"{num} ⬅", callback_data = f"draft_{num - 1}"),
				 InlineKeyboardButton(f"К первому", callback_data = f"draft_0")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
		query.edit_message_text(f"Кому: <code>{ast.literal_eval(drafts[num])[0]}</code>\n\n{ast.literal_eval(drafts[num])[2]}", parse_mode = ParseMode.HTML, reply_markup = reply_markup)

	elif (data == TEAM1 or data == TEAM2 or data == TEAM3 or data == TEAM4 or data == TEAM5 or
		  data == TEAM6 or data == TEAM7 or data == TEAM8 or data == TEAM9 or data == TEAM10):
		inline_keyboard = []
		for person in TEAM_PERSONS[data]:
			inline_keyboard.append([InlineKeyboardButton(person, callback_data = person)])
		inline_keyboard.append([InlineKeyboardButton("Назад ↩", callback_data = "back_gratitude")])
		reply_markup = InlineKeyboardMarkup(inline_keyboard)
		query.edit_message_text("Выбери человека, которого ты хочешь поблагодарить или поддержать.", reply_markup = reply_markup)
	elif (data == "back_gratitude"):
		query.edit_message_text("Мы рады, что у тебя есть ресурс поддержать команду💜\n\nВыбери, человеку из какой комнадочки ты хочешь написать письмо.",
								reply_markup = gratitude.get_gratitude_inline_keyboard())

	elif data in sum(TEAM_PERSONS.values(), []):
		context.user_data[TO] = data
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton("Подписать", callback_data = "Подписать"),
					InlineKeyboardButton("Анонимно", callback_data = "Анонимно")
				],
			]
			)
		query.edit_message_text("Супер! Хочешь подписать письмо или отправить анонимно?", reply_markup = reply_markup)

	elif (data == "Подписать" or data == "Анонимно"):
		context.user_data[FROM] = data
		#logger.info('user_data: %s', context.user_data)
		query.edit_message_text("Договорились. Напиши письмо, и мы доставим его адресату💌")
		return (MESSAGE)

	elif (data == "Отправляем"):
		query.edit_message_text("Секундочку, бот занят отправкой письма...")
		try:
			user_id = googlesheets.get_user_id_from_grattitude_name(context.user_data[TO])
			if (context.user_data[FROM] != "Анонимно"):
				context.user_data[FROM] = googlesheets.get_user_name(query.from_user.id)
				text = f"Ку-ку! {context.user_data[FROM]} приcлал(а) тебе письмо 💌\n\n"
			else:
				text = "Ку-ку! Тебе пришло письмо от человека из команды 💌\n\n"
			text += f"<i>{context.user_data[MESSAGE]}</i>"
			text += "\n\nХочешь сохранить письмо в <b>Дневник📆</b>, чтобы в любой момент перечитать его?"
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Да", callback_data = "save_message_yes"),
					 InlineKeyboardButton("Нет", callback_data = "save_message_no")],
				])
			context.bot.send_message(chat_id = user_id, text = text, parse_mode = ParseMode.HTML, reply_markup = reply_markup)
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
			query.edit_message_text("Спасибо, что заботишься о команде. Письмо уже улетело адресату.", reply_markup = reply_markup)
		except:
			googlesheets.save_message(context.user_data[TO], context.user_data[MESSAGE])
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
			query.edit_message_text("Спасибо, что заботишься о команде. Письмо уже улетело адресату.", reply_markup = reply_markup)
	elif (data == "save_message_yes" or data == "save_message_no"):
		if (data == "save_message_yes"):
			message = str(query.message.text)
			message = message[message.find("\n\n") + 1:]
			message = message[:(message.rfind("\n\n"))]
			logger.info('user_data: %s', message)
			googlesheets.save_message(googlesheets.get_user_name(query.from_user.id), message[1:])
			query.edit_message_text("Твоё письмо сохранено.")
		else:
			query.edit_message_text("Хорошо!")


	elif (data == "Пока в черновики"):
		query.edit_message_text("Сохраняем твоё письмо в черновики...")
		googlesheets.save_to_drafts(query.from_user.id, context.user_data)
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
		query.edit_message_text("Всё отлично! Возвращайся, когда будешь готов(а)", reply_markup = reply_markup)


	# ----- ДНЕВНИК ----- #
	elif (data == "DIARY_BUTTON"):
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
			[
				InlineKeyboardButton("Заметки", callback_data = "notes"),
				InlineKeyboardButton("Письма", callback_data = "letters")
			],

			[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
		])
		query.edit_message_text("<i>Рефлексия</i> — классный инструмент самоподдержки. Здесь все твои заметки о состоянии и письма благодарности от команды.\n\nЧто ты хочешь перечитать?", parse_mode = ParseMode.HTML,
							reply_markup = reply_markup)
	elif (data == "notes"):
		notes = googlesheets.get_notes(query.from_user.id)
		if (notes == 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
						[InlineKeyboardButton("Назад в главное меню", callback_data = MENU),]
					])
			query.edit_message_text(text = f"У тебя пока ещё нет записей. Они начнут появяться, как только ты начнёшь проходить чекапы!", parse_mode = ParseMode.HTML, reply_markup = reply_markup)
		else:
			notes_by_date = {}
			for note in notes:
				note = ast.literal_eval(str(note))
				note[3] = datetime.strptime(note[3], "%Y/%m/%d").date()
				notes_by_date[note[3]] = {0: note[0], 1: note[1], 2: note[2]}
			context.user_data[0] = notes_by_date
			logger.info('user_data: %s', notes_by_date)
			dates = list(notes_by_date.keys())
			x, y, moods = [], [], []
			i = -1
			while(dates[i]):
				x.append(dates[i])
				y.append(int(notes_by_date[dates[i]][0]))
				moods.append(notes_by_date[dates[i]][1])
				i -= 1
				if ((i < -len(dates)) or (len(x) == 5)):
					break
			makeplot(x, y)
			x1 = x[-1].strftime("%Y-%m-%d")
			x2 = x[0].strftime("%Y-%m-%d")
			moods = sum(moods, [])
			c = Counter(moods)
			i = 0
			moods = ""
			try:
				c_moods = c.most_common(2)
			except:
				c_moods = c.most_common(1)
			while (list(c.keys())[i]):
				moods += f"и <code>{list(c_moods[i])[0]}</code> "
				if (i < 1 and i < len(c_moods) - 1):
					i += 1
				else:
					break
			text = ""
			for day in x:
				fday = day.strftime("%Y-%m-%d")
				if (notes_by_date[day][2] != 'null'):
					text += f"<code>{fday}</code>\n<b>Ты чувствовал(а) в этот день:</b> <i>{', '.join(notes_by_date[day][1])}</i>\n{notes_by_date[day][2]}\n\n"
				else:
					text += f"<code>{fday}</code>\n<b>Ты чувствовал(а) в этот день:</b> <i>{', '.join(notes_by_date[day][1])}</i>\n\n"
			if (len(dates) > 5):
				if (len(dates) <= 10):
					x_next = str(dates[0].strftime("%Y-%m-%d"))[5:]
				else:
					x_next = str(dates[-10].strftime("%Y-%m-%d"))[5:]
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
							[InlineKeyboardButton(f"⬅{x_next} - {str(x1)[5:]}", callback_data = "week_5")],
							[InlineKeyboardButton("Назад в главное меню", callback_data = MENU),]
						])
			else:
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
							[InlineKeyboardButton("Назад в главное меню", callback_data = MENU),]
						])
			query.delete_message()
			context.bot.send_photo(chat_id = query.from_user.id, photo = open("img/checkup.png", 'rb'), caption = f"<code>{x1} – {x2}</code>\n\nЧаще всего за это время ты испытавал(а): {moods[2:]}", parse_mode = ParseMode.HTML)
			context.bot.send_message(chat_id = query.from_user.id, text = f"{text}", parse_mode = ParseMode.HTML, reply_markup = reply_markup)

	elif (re.search("^week_\d{1,}$", data)):
		n = int(data[5:])
		notes_by_date = context.user_data[0]
		dates_0 = list(notes_by_date.keys())
		dates = list(notes_by_date.keys())
		if (n != 0):
			dates = dates[:-n]
		x, y, moods = [], [], []
		i = -1
		while(dates[i]):
			x.append(dates[i])
			y.append(int(notes_by_date[dates[i]][0]))
			moods.append(notes_by_date[dates[i]][1])
			i -= 1
			if ((i < -len(dates)) or (len(x) == 5)):
				break
		makeplot(x, y)
		x1 = x[-1].strftime("%Y-%m-%d")
		x2 = x[0].strftime("%Y-%m-%d")
		moods = sum(moods, [])
		c = Counter(moods)
		i = 0
		moods = ""
		try:
			c_moods = c.most_common(2)
		except:
			c_moods = c.most_common(1)
		while (list(c.keys())[i]):
			moods += f"и <code>{list(c_moods[i])[0]}</code> "
			if (i < 1 and i < len(c_moods) - 1):
				i += 1
			else:
				break
		text = ""
		for day in x:
			fday = day.strftime("%Y-%m-%d")
			if (notes_by_date[day][2] != 'null'):
				text += f"<code>{fday}</code>\n<b>Ты чувствовал(а) в этот день:</b> <i>{', '.join(notes_by_date[day][1])}</i>\n{notes_by_date[day][2]}\n\n"
			else:
				text += f"<code>{fday}</code>\n<b>Ты чувствовал(а) в этот день:</b> <i>{', '.join(notes_by_date[day][1])}</i>\n\n"
		if (len(dates) > 5):
			x_prev = str(dates_0[-n + 5].strftime("%Y-%m-%d"))[5:]
			if (len(dates) <= 10):
				x_next = str(dates[0].strftime("%Y-%m-%d"))[5:]
			else:
				x_next = str(dates[-10].strftime("%Y-%m-%d"))[5:]
			if (n == 0):
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
							[InlineKeyboardButton(f"⬅{x_next} - {str(x1)[5:]}", callback_data = "week_5")],
							[InlineKeyboardButton("Назад в главное меню", callback_data = MENU),]
						])
			else:
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
							[InlineKeyboardButton(f"⬅{x_next} - {str(x1)[5:]}", callback_data = f"week_{n + 5}"),
							InlineKeyboardButton(f"➡{str(x1)[5:]} - {x_prev}", callback_data = f"week_{n - 5}")],
							[InlineKeyboardButton("Назад в главное меню", callback_data = MENU),]
						])
		else:
			x_prev = str(dates_0[-n + 5].strftime("%Y-%m-%d"))[5:]
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
						[InlineKeyboardButton(f"➡{str(x1)[5:]} - {x_prev}", callback_data = f"week_{n - 5}")],
						[InlineKeyboardButton("Назад в главное меню", callback_data = MENU),]
					])

		context.bot.edit_message_media(media = InputMediaPhoto(media=open('img/checkup.png', 'rb'), caption=f'<code>{x1} – {x2}</code>\n\nЧаще всего за это время ты испытавал(а): {moods[2:]}', parse_mode = ParseMode.HTML), chat_id = query.from_user.id, message_id = query.message.message_id - 1)
		query.edit_message_text(f"{text}", parse_mode = ParseMode.HTML, reply_markup = reply_markup)


	elif (data == "letters"):
		letters = googlesheets.get_letters(query.from_user.id)
		context.user_data[0] = letters
		if (letters == 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
			query.edit_message_text("У тебя пока нет писем от командочки. Но ты можешь попросить поддержать тебя в разделе <b>Поддержка ✊</b>",  parse_mode = ParseMode.HTML, reply_markup = reply_markup)
		else:
			count = len(letters)
			if count > 1:
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[
						InlineKeyboardButton(f"К последнему", callback_data = f"letter_{count - 1}"),
						InlineKeyboardButton("2 ➡", callback_data = "letter_1")],
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
			else:
				reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
			query.edit_message_text(letters[0], reply_markup = reply_markup)

	elif (re.search("^letter_\d{1,}$", data)):
		letters = context.user_data[0]
		count = len(letters)
		num = int((re.search("\d{1,}", data)).group(0))
		if (num != count - 1 and num > 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton(f"{num} ⬅", callback_data = f"letter_{num - 1}"),
					InlineKeyboardButton(f"{num + 2} ➡", callback_data = f"letter_{num + 1}")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
		elif (num == 0):
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton(f"К последнему", callback_data = f"letter_{count - 1}"),
					InlineKeyboardButton("2 ➡", callback_data = "letter_1")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
		else:
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[InlineKeyboardButton(f"{num} ⬅", callback_data = f"letter_{num - 1}"),
				InlineKeyboardButton(f"К первому", callback_data = f"letter_0")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
		query.edit_message_text(letters[num], reply_markup = reply_markup)

	# ----- ПАМАГИТИ ----- #
	elif (data == "HELP_BUTTON"):
		inline_keyboard, line1, line2 = [], [], []
		context.user_data[HELP] = []
		context.user_data[INDEX] = []
		for i in range(1, 13):
			if i <= 6:
				line1.append(InlineKeyboardButton(f"{i}", callback_data = f"{i}"))
			else:
				line2.append(InlineKeyboardButton(f"{i}", callback_data = f"{i}"))
		inline_keyboard.append(line1)
		inline_keyboard.append(line2)
		inline_keyboard.append([InlineKeyboardButton("Другое", callback_data = "other"), InlineKeyboardButton("Сохранить", callback_data = "save_help")])
		inline_keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data = MENU)])
		reply_markup = InlineKeyboardMarkup(inline_keyboard)
		query.edit_message_text(needhelp.HELP_TEXT, reply_markup = reply_markup)

	elif (data == "other"):
		query.edit_message_text('Напиши, какой поддержки тебе бы хотелось от команды')
		return (HELP)

	elif (re.search("^\d{1,}$", data)):
		context.user_data[HELP].append(needhelp.HELP_LIST[int(data)])
		context.user_data[INDEX].append(data)
		inline_keyboard, line1, line2 = [], [], []
		for i in range(1, 13):
			if i <= 6:
				line1.append(InlineKeyboardButton(f"{i}", callback_data = f"{i}"))
			else:
				line2.append(InlineKeyboardButton(f"{i}", callback_data = f"{i}"))
		inline_keyboard.append(line1)
		inline_keyboard.append(line2)
		inline_keyboard.append([InlineKeyboardButton("Изменить ответ", callback_data = "HELP_BUTTON")])
		inline_keyboard.append([InlineKeyboardButton("Другое", callback_data = "other"), InlineKeyboardButton("Сохранить", callback_data = "save_help")])
		inline_keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data = MENU)])
		reply_markup = InlineKeyboardMarkup(inline_keyboard)
		text = needhelp.HELP_TEXT + f"\n\nТы выбрал(а): <i>{', '.join(context.user_data[INDEX])}</i>"
		query.edit_message_text(text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)

	elif (data == "save_help"):
		if (len(context.user_data[HELP]) == 0):
			inline_keyboard, line1, line2 = [], [], []
			for i in range(1, 13):
				if i <= 6:
					line1.append(InlineKeyboardButton(f"{i}", callback_data = f"{i}"))
				else:
					line2.append(InlineKeyboardButton(f"{i}", callback_data = f"{i}"))
			inline_keyboard.append(line1)
			inline_keyboard.append(line2)
			inline_keyboard.append([InlineKeyboardButton("Изменить ответ", callback_data = "HELP_BUTTON")])
			inline_keyboard.append([InlineKeyboardButton("Другое", callback_data = "other"), InlineKeyboardButton("Сохранить", callback_data = "save_help")])
			inline_keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data = MENU)])
			reply_markup = InlineKeyboardMarkup(inline_keyboard)
			text = needhelp.HELP_TEXT + f"\n\nТы выбрал(а): <i>{', '.join(context.user_data[INDEX])}</i>"
			query.edit_message_text(text, reply_markup = reply_markup, parse_mode = ParseMode.HTML)
		else:
			now = datetime.now()
			context.user_data[TODAY] = now.strftime("%Y/%m/%d")
			logger.info('user_data: %s', context.user_data)
			googlesheets.save_help_data(context.user_data, query.from_user.id)
			reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
			])
			query.edit_message_text(f'Спасибо, {googlesheets.get_name_by_id(query.from_user.id)}! Просить поддержки нормально, с тобой всё в порядке❤️', reply_markup = reply_markup)


	# ----- ПОЛЕЗНОСТИ ----- #
	elif (data == "UTILITY_BUTTON"):
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[InlineKeyboardButton("💪🏽 Физическое здоровье", callback_data = "utility_01")],
				[InlineKeyboardButton("😬 Поддержка при неопределённости", callback_data = "utility_02")],
				[InlineKeyboardButton("💨 Дыхательные упражнения", callback_data = "utility_03")],
				[InlineKeyboardButton("🔮 Жизнь в новой реальности", callback_data = "utility_04")],
				[InlineKeyboardButton("☺️ Испытывать счастье в деятельности", callback_data = "utility_05")],
				[InlineKeyboardButton("❤️ Как общаться", callback_data = "utility_06")],
				[InlineKeyboardButton("💰 Про финансы", callback_data = "utility_07")],
				[InlineKeyboardButton("🤓 Про развитие", callback_data = "utility_08")],
				[InlineKeyboardButton("✈️ Про эмиграцию", callback_data ="utility_09")],
				[InlineKeyboardButton("🏖 Что поделать на досуге", callback_data ="utility_10")],
				[InlineKeyboardButton("🙏🏼 Как быть полезным", callback_data = "utility_11")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)]
		])
		query.edit_message_text("Привет, друллега! Собрали для тебя разные материалы и ресурсы, которые помогут чувствовать себе увереннее в турбулентное время. Да и по жизни. Здесь и про здоровье, и про бабки, и про тревожки. \n\n❗ Лучше включить VPN, так как есть ссылки на запрещёнку.", reply_markup = reply_markup)

	elif (re.search("^utility_\d{1,}$", data)):
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[InlineKeyboardButton("Назад в Полезности", callback_data = "UTILITY_BUTTON")],
				[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
		])
		query.edit_message_text(utility.UTILITY_MENU[data], parse_mode = ParseMode.HTML, reply_markup = reply_markup)


	# ----- НАСТРОЙКИ ----- #
	elif (data == "SETTINGS_BUTTON"):
		reply_markup = InlineKeyboardMarkup(inline_keyboard = [
			[InlineKeyboardButton("Имя", callback_data = "name")],
			[InlineKeyboardButton("Корпоративная почта", callback_data = "mail")],
			[InlineKeyboardButton("Время чекапа", callback_data = "checkup_yes")],
			[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)]
		])
		query.edit_message_text("Салют!💥\n\nЧто ты хочешь изменить?",
							reply_markup = reply_markup)
	elif (data == "name" or data == "mail" or data == "time" or data == "frequency"):
		if (data == "name"):
			query.edit_message_text('Как ты хочешь, чтобы бот обращался к тебе? Введи имя или прозвище:')
			return (NAME)
		elif (data == "mail"):
			query.edit_message_text('Введи новый адрес корпоративной почты!')
			return(MAIL)
	elif (data == MENU):
		query.edit_message_text(menu.MENU_TEXT ,parse_mode = ParseMode.HTML, reply_markup = menu.get_menu_inline_keyboard())

def change_name(update: Update, context: CallbackContext):
	googlesheets.update_name(update.message.from_user.id, update.message.text)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
	update.message.reply_text("Принято👌", reply_markup = reply_markup)
	return ConversationHandler.END

def change_mail(update: Update, context: CallbackContext):
	mail = validators.mail_validator(text = update.message.text)
	if mail == -1:
		update.message.reply_text('Упс, кажется, это не корпоративный e-mail esprezo. Проверь, всё ли верно?')
		return (MAIL)
	if googlesheets.check_mail_duplication(update.message.text) == 0:
		update.message.reply_text('Этот почтовый адрес уже зарегистрирован!\nЕсли это твой e-mail, и ты ещё не проходил(а) регистрацию, пожалуйста, напиши @vlatskaya. Она со всем разберётся. 💪')
		return (MAIL)
	googlesheets.update_mail(update.message.from_user.id, update.message.text)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
					[InlineKeyboardButton("Назад в главное меню", callback_data = MENU)],
				])
	update.message.reply_text("Принято👌", reply_markup = reply_markup)
	return ConversationHandler.END

def get_message(update: Update, context: CallbackContext):
	message =  update.message.text
	context.user_data[MESSAGE] = message
	logger.info('user_data: %s', context.user_data)
	reply_markup = InlineKeyboardMarkup(inline_keyboard = [
				[
					InlineKeyboardButton("Отправляем", callback_data = "Отправляем"),
					InlineKeyboardButton("Пока в черновики", callback_data = "Пока в черновики")
				],
			]
			)
	update.message.reply_text("Хочешь отправить письмо сейчас или сохранить в черновики?", reply_markup = reply_markup)
	return ConversationHandler.END


# polling
def main():
	bot = Bot(
		token = BOT_API_KEY
	)
	updater = Updater(
		bot = bot,
		use_context=True
	)
	j = updater.job_queue
	print(updater.bot.get_me())
	dp = updater.dispatcher
	j.set_dispatcher(dp)
	print(j)
	start_handler = ConversationHandler(
		entry_points = [CommandHandler('start', start.start)],
		states = {
			NAME: [MessageHandler(Filters.text, start.name_handler, pass_user_data = True)],
			MAIL: [MessageHandler(Filters.text, start.mail_handler, pass_user_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	report_handler = ConversationHandler(
		entry_points = [CommandHandler('report', report.report)],
		states = {
			TEXT: [MessageHandler(Filters.text, report.send_report, pass_user_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	menu_handler = CommandHandler('menu', menu.menu)
	button_handler = CallbackQueryHandler(button_reply_handler, pass_chat_data = True,  pattern="^(?![-|+]0[0-9]:00$|name$|mail$|Анонимно$|Подписать$|Другое$|Хочу$|other$)")
	dp.add_handler(start_handler)
	dp.add_handler(report_handler)
	dp.add_handler(menu_handler)
	dp.add_handler(button_handler)
	checkup_handler = ConversationHandler(
		entry_points = [CallbackQueryHandler(button_reply_handler, pass_chat_data = True, pattern="^[-|+]0[0-9]:00$")],
		states = {
			TIME: [MessageHandler(Filters.text, checkup.checkup_time_handler, pass_chat_data = True, pass_job_queue = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	real_checkup_handler = ConversationHandler(
		entry_points = [CallbackQueryHandler(button_reply_handler, pass_chat_data = True, pattern="^Другое$")],
		states = {
			MOOD: [MessageHandler(Filters.text, checkup.other_mood, pass_chat_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	real_checkup_handler_2 = ConversationHandler(
		entry_points = [CallbackQueryHandler(button_reply_handler, pass_chat_data = True, pattern="^Хочу$")],
		states = {
			NOTES: [MessageHandler(Filters.text, checkup.handle_notes, pass_chat_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	settings_handler = ConversationHandler(
		entry_points = [CallbackQueryHandler(button_reply_handler, pass_chat_data = True, pattern="^(name$|mail$)")],
		states = {
			NAME: [MessageHandler(Filters.text, change_name, pass_user_data = True)],
			MAIL: [MessageHandler(Filters.text, change_mail, pass_user_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	gratitude_handler = ConversationHandler(
		entry_points = [CallbackQueryHandler(button_reply_handler, pass_chat_data = True, pattern="^(Анонимно$|Подписать$)")],
		states = {
			MESSAGE: [MessageHandler(Filters.text, get_message, pass_chat_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	help_handler = ConversationHandler(
		entry_points = [CallbackQueryHandler(button_reply_handler, pass_chat_data = True, pattern="^(other$)")],
		states = {
			HELP: [MessageHandler(Filters.text, needhelp.other_help, pass_chat_data = True)],
		},
		fallbacks = [CommandHandler('cancel', cancel_handler)],
	)
	dp.add_handler(checkup_handler)
	dp.add_handler(real_checkup_handler)
	dp.add_handler(real_checkup_handler_2)
	dp.add_handler(gratitude_handler)
	dp.add_handler(help_handler)
	dp.add_handler(settings_handler)
	dp.add_handler(button_handler)

	# Начать бесконечную обработку входящих сообщений
	updater.start_polling()
	j.start()
	updater.idle()

if __name__ == '__main__':
	main()



