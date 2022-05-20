from datetime import datetime
import googlesheets

def mail_validator(text: str):
	esprezo_mails = googlesheets.get_mails()
	try:
		esprezo_mails.index(str(text))
		return (1)
	except:
		return(-1)
	#if text.find("@esprezo.ru") == -1:
	#	return (-1)
	#else:
	#	return (1)

def time_validator(text: str):
	try:
		time = datetime.strptime(text, '%H:%M')
	except:
		return (-1)
	return (time.strftime('%H:%M'))
