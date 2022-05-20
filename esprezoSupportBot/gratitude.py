from telegram import Update, ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext


TEAM1 = "partners"
TEAM2 = "scenarists"
TEAM3 = "designers"
TEAM4 = "MPRs"
TEAM5 = "projects"
TEAM6 = "education"
TEAM7 = "hr"
TEAM8 = "marketing"
TEAM9 = "OMs"
TEAM10 = "MRAK"
DRAFTS = "drafts"
MENU = "menu"

TEAM_PERSONS = {
	TEAM1: ["Марк Хлынов", "Амир Абдуллаев", "Лиля Бикбова", "Даня Фишкин"],
	TEAM2: ["Лена Влацкая", "Ксеня Наринская", "Даша Хаустова", "Лика Лагошенко", "Маша Савотикова", "Маша Седик"],
	TEAM3: ["Даша Черевкова", "Настя Бажанова", "Диана Николаева", "Регина Назарян", "Влад Кузнецов", "Олеся Ткаченко", "Юля Липунцова", "Вика Борисова"],
	TEAM4: ["Эд Мелкумян", "Антон Колосс", "Андрей Пискунов", "Артём Калачихин"],
	TEAM5: ["Артемий Козуб", "Света Максимова"],
	TEAM6: ["Настя Воробьёва", "Ника Валиева", "Наташа Баннова"],
	TEAM7: ["Алёна Шарикова"],
	TEAM8: ["Яков Чайкин", "Настя Стрельцова", "Влада Мамонова", "Настя Грабович", "Саша Бестужева"],
	TEAM9: ["Дима Акопян", "Света Петровская"],
}

TEAM_BUTTONS = {
	TEAM1: "Партнёры",
	TEAM2: "Сценаристы",
	TEAM3: "Дизайнеры",
	TEAM4: "МПРы",
	TEAM5: "Проджекты",
	TEAM6: "Обучение",
	TEAM7: "HR",
	TEAM8: "Маркетинг",
	TEAM9: "ОМы",
	TEAM10: "МРАК",
	DRAFTS: "Мои черновики",
	MENU: "Назад в главное меню",
}

def get_gratitude_inline_keyboard():
	inline_keyboard = [
		[InlineKeyboardButton(TEAM_BUTTONS[TEAM1], callback_data = TEAM1), InlineKeyboardButton(TEAM_BUTTONS[TEAM2], callback_data = TEAM2)],
		[InlineKeyboardButton(TEAM_BUTTONS[TEAM3], callback_data = TEAM3), InlineKeyboardButton(TEAM_BUTTONS[TEAM4], callback_data = TEAM4)],
		[InlineKeyboardButton(TEAM_BUTTONS[TEAM5], callback_data = TEAM5), InlineKeyboardButton(TEAM_BUTTONS[TEAM6], callback_data = TEAM6)],
		[InlineKeyboardButton(TEAM_BUTTONS[TEAM7], callback_data = TEAM7), InlineKeyboardButton(TEAM_BUTTONS[TEAM8], callback_data = TEAM8)],
		[InlineKeyboardButton(TEAM_BUTTONS[TEAM9], callback_data = TEAM9)],
		[InlineKeyboardButton(TEAM_BUTTONS[DRAFTS], callback_data = DRAFTS)],
		[InlineKeyboardButton(TEAM_BUTTONS[MENU], callback_data = MENU)]
	]
	return (InlineKeyboardMarkup(inline_keyboard))
