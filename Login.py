import random
import threading
import re
import requests
import pickle
import urllib
from bs4 import BeautifulSoup
import csv
import time
import urllib
import fake_useragent
import codecs
import os
import json
from os import sys
from datetime import date
from datetime import datetime
from GlobalData import globalData

class loginClass():
	def GetGlobalToken(self, mainPagesoupStr):

		WindowGvarsIndex = mainPagesoupStr.find('window.gvars')
		if (WindowGvarsIndex < 0):
			return False
		StartJSONIndex = mainPagesoupStr.find('{', WindowGvarsIndex)
		StopJSONIndex = mainPagesoupStr.find('};', StartJSONIndex) + 1
		JsonData = mainPagesoupStr[StartJSONIndex:StopJSONIndex]

		#	print(JsonData)
		dict_from_json = json.loads(JsonData)
		user_dict = dict_from_json['user']
		print(user_dict)
		print('token=' + user_dict['actions_token'])
		self.globaltoken = user_dict['actions_token']

	def LoginProcess(self):
		user = fake_useragent.UserAgent().random

		header = {
			'user-agent': user
			#	'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.135 YaBrowser/21.6.3.757 Yowser/2.5 Safari/537.36'
		}
		html = self.session.get(globalData.HOST)
		print('Get req: status code is' + str(html.status_code))
		if html.status_code == 200:
			#		FindList = codecs.open('FirstGet.html','w','utf-8-sig')
			#		FindList.write(html.text)
			#		FindList.close()
			soup = BeautifulSoup(html.text, 'html.parser')
			if soup is None:
				self.ErrCodeVal = 1
				return False
			link2LoginPage = soup.find('a', class_='header_login')
			if link2LoginPage is None:
				self.ErrCodeVal = 0
				self.GetGlobalToken(html.text)
				return True
			html = self.session.get(globalData.HOST + link2LoginPage.get('href'))
			print('Get req: status code is' + str(html.status_code))
			if html.status_code == 200:
				#			FindList = codecs.open('SecondGet.html','w','utf-8-sig')
				#			FindList.write(html.text)
				#			FindList.close()
				#		sys.exit()
				soup = BeautifulSoup(html.text, 'html.parser')
				if soup is None:
					self.ErrCodeVal = 2
					return False

				loginForm = soup.find('form')
				if loginForm is None:
					self.ErrCodeVal = 3
					return False

				ValOfToken = loginForm.find('input', {'name': 'token'}).get('value')

				data = {
					"email": "email@domen.ru",
					"password": "yourpassword",
					"token": ValOfToken
				}

				linkToLogin = str(loginForm.get('action'))
				if linkToLogin is None:
					self.ErrCodeVal = 4
					return False
				if linkToLogin.find('login') < 0:
					self.ErrCodeVal = 5
					return False
				time.sleep(0.5)
				html = self.session.post(globalData.HOST + linkToLogin, data=data, headers=header)
				print('Post Login req: status code is' + str(html.status_code))
				if html.status_code == 200:
					with open('data.pickle', 'wb') as f:
						pickle.dump(self.session, f)
					self.GetGlobalToken(html.text)
					#				FindList = codecs.open('LoginPost.html', 'w', 'utf-8-sig')
					#				FindList.write(html.text)
					#				FindList.close()
					#				sys.exit()
					return True
				else:
					return False
			else:
				return False

	def __init__(self):
		self.HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0',
				   'accept': '*/*'}
		if os.path.exists('data.pickle') == True:
			with open('data.pickle', 'rb') as f:
				self.session = pickle.load(f)
		else:
			self.session = requests.Session()

		user = fake_useragent.UserAgent().random

		self.header = {
			#	'user-agent': user
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.135 YaBrowser/21.6.3.757 Yowser/2.5 Safari/537.36'

		}
		self.ErrCodeVal = 0
		self.Result = self.LoginProcess()



if __name__ == '__main__':
	login = loginClass()
	if login.Result:
		print('OK')
	else:
		print('Error occurred')


