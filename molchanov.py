# molchanov.py
import requests
import os
import json

key = 'TOKEN_BOT'

token = os.getenv(key, default=None) # примерно, точно не помню как


URL = 'https://api.telegram.org/bot' + token + '/'

def get_answer(r):
	"""r = requests.get('https://api.github.com/events')
				r = r.json()"""
	#print(r)
	with open('answer.json', 'w') as file:
		json.dump(r, file, indent=2, ensure_ascii=False)
	print('Сообщение отправлено')

def get_updates():
	url = URL + 'getUpdates'
	r = requests.get(url)
	return r.json()

def get_message():
	data = get_updates()
	chat_id = data['result'][-1]['message']['chat']['id']
	message_text = data['result'][-1]['message']['text']

	message = {
	'chat_id': chat_id,
	'text': message_text
	}
	return message

def send_message(chat_id, text='Wait a second, please...'):
	url = URL + 'sendmessage?chat_id={}&text={}'.format(chat_id, text)
	r = requests.get(url)
	r = r.json()
	get_answer(r)
	return 
	
	


def main():
	d = get_updates()
	#with open('updates.json', 'w') as file:
	#	json.dump(d, file, indent=2, ensure_ascii=False)
	send_message(196584706, 'РОБЕ')


if __name__ == '__main__':
	main()