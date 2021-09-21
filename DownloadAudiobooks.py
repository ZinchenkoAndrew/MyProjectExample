import random
import threading
import re
import requests
#from clint.textui import progress
from tqdm import tqdm
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
from login import loginClass
from shelf import Shelf
from GlobalData import globalData


class downloadAudiobooks():
	def __init__(self, session):
		self.ErrCodeVal = 0
		self.session = session

	def getnAbooksInDir(self):
		listdir = os.listdir(globalData.MP3_DIR)
		#print(list)
		return len(listdir)
	def save_file_from_www(self, linkTo, NameOfBook, book_key):
		res = True
		book_dir = globalData.MP3_DIR + "/" + NameOfBook
		filename = linkTo.split('/')[-1]
		fullpathtomp3 = book_dir+"/"+filename
		if os.path.exists(fullpathtomp3) == False:
				resp = self.session.get(linkTo, headers={'referer': (globalData.HOST+'/')}, cookies={'book_key': book_key}, stream=True)
				total_length = int(resp.headers.get('content-length', 0))
				with open(fullpathtomp3, 'wb') as file, tqdm(
						desc=fullpathtomp3,
						total=total_length,
						unit='iB',
						unit_scale=True,
						unit_divisor=1024,
				) as bar:
					for data in resp.iter_content(chunk_size=1024):
						size = file.write(data)
						bar.update(size)

				if resp.status_code != 200:
					print('error:', r.status_code)
					res = False
				else:
#					open(fullpathtomp3, 'wb').write(r.content)
					res = True
		return res


	def DownloadAbook(self, locallinkBook):

		self.ErrCodeVal = 0
		res = False
		print('Скачивание книги... ')
		print('Link: ' + globalData.HOST + locallinkBook)
		time.sleep(0.5)
		html = self.session.get(globalData.HOST + locallinkBook)
		RefererLink = globalData.HOST + locallinkBook

		mainPagesoup = BeautifulSoup(html.text, 'html.parser')

		mainPagesoupStr = html.text
		BookControllerIndex = mainPagesoupStr.find('BookController.enter')
		if (BookControllerIndex < 0):
			self.ErrCodeVal = 1
			return res
		StartJSONIndex = mainPagesoupStr.find('(', BookControllerIndex) + 1
		StopJSONIndex = mainPagesoupStr.find(');', StartJSONIndex)
		JsonData = mainPagesoupStr[StartJSONIndex:StopJSONIndex]

#					print(JsonData)
		dict = json.loads(JsonData)

		merged_playlist = dict['merged_playlist']
		if len(merged_playlist) > 0:
			playlist = merged_playlist
		else:
			playlist = dict['playlist']
		NameOfBook = book['name']
		book_dir = globalData.MP3_DIR + "/" + NameOfBook
		if len(playlist) > 0:
			if os.path.exists(book_dir) == False:
				os.mkdir(book_dir)
#					print(NameOfBook)
		for list_item in playlist:
			DownloadURL = str(list_item['url'])
			print(DownloadURL)

			while True:
				try:
					res = self.save_file_from_www(DownloadURL, NameOfBook, book_key)
				except Exception as e:
					print('Error download {0}'.format(e))
					time.sleep(5)
					continue
				else:
					if not res:
						continue
					break

		res = True

		self.SendPlayAbookById(id)
		print('Книга скачана успешно')
		return res


	def SendPlayAbookById(self,id):
		locallinkPlayBook = '/play/id/' + id + '/'
		time.sleep(0.5)
		html = self.session.get(globalData.HOST + locallinkPlayBook)
		if html.status_code == 200:
			return True
		else:
			return False

	def SendPlayAbookList(self, abook_list):
		counter = 0
		for abook in abook_list:
			abook_split = abook.split(':')
			if self.SendPlayAbookById(abook_split[0]) == True:
				counter += 1
		return counter

	def DownloadAbookList(self, abook_list):
		counter = 0
		for abook in abook_list:
			abook_split = abook.split(':')
			if self.DownloadAbook(abook_split[1]) == True:
				counter += 1
		return counter

if __name__ == '__main__':
	login = loginClass()
	if login.Result:
		download = downloadAudiobooks(login.session)
		shelf = Shelf(login.session, login.globaltoken)
		shelf.MakeListABooksOnShelf()
		download.SendPlayAbookList(shelf.AbooksOnShelf)
#		download.DownloadAbookList(shelf.AbooksOnShelf)
#		download.getnAbooksInDir()
#		download.SendPlayAbookById('33817')
		print('OK')
	else:
		print('Error occured')


