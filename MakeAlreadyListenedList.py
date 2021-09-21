import random
import threading
import re
import requests
import pickle
import urllib
from bs4 import BeautifulSoup
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
from GlobalData import globalData

class makeAlreadyListenedList():
	AlreadyListenedAbooks = []

	def FindAlreadyListenedProcess(self):

		self.AlreadyListenedAbooks.clear()

		self.ErrCodeVal = 0


		page = 1
		AllBooks = 0
		ProcessBooks = 0
		print('\r\n************Построение списка уже слушаемых/прослушанных книг***************************')
		while (1):

			FindUrl = globalData.HOST + globalData.link2AlreadyListenedPage + '/?page='+str(page)
#			print(FindUrl)
			time.sleep(0.5)
			html = self.session.get(FindUrl)

			if html.status_code == 200:
	#			FindList = codecs.open('AlreadyListenedResultFind.html','w','utf-8-sig')
	#			FindList.write(html.text)
	#			FindList.close()
				FindListsoup = BeautifulSoup(html.text, 'html.parser')
				if FindListsoup is None:
					ErrCodeVal = 1
					break
				liList = FindListsoup.find_all('span', class_='bookitem')
	#			print('liList='+str(liList))

				if liList is None or len(liList) == 0:
					ErrCodeVal = 2
					break

				if page == 1:
					nBooksTag = FindListsoup.find('div',class_='user_shelf_books_count')
					if nBooksTag is None:
						ErrCodeVal = 3
						break
					nBooksStr = nBooksTag.text.replace(' ', '')
					AllBooks = int((re.findall(r'\d+', nBooksStr)[0]))
				#Список ссылок на книги на полке
				BooksPerPage = len(liList)
#				print(
#					'books ' + str(ProcessBooks+1) + '...' + str(ProcessBooks + BooksPerPage ) + '---------------------------------')

				for li in liList:
					booknametag = li.find('a',class_='bookitem_name')
					reader = li.find('div',class_='bookitem_meta_block icon_reader')
					NameOfReader = reader.find('a',class_='bookitem_meta_link').text
					NameOfBook = booknametag.text.strip()

#					print('Abook: ' + NameOfBook + ' reader: ' + NameOfReader)

					string4add = NameOfBook+':'+NameOfReader
#					with open('list.txt','a+',encoding='utf-8') as f:
#						f.write(string4add+'\r\n')
					if self.AlreadyListenedAbooks.count(string4add) == 0:
						self.AlreadyListenedAbooks.append(string4add)  #После успешной обработки пользователя добавляем его в игнор для более быстрой обработки в будущем
					else:
						pass
#						print('Name Of book is already present:' + NameOfBook)
#						index = self.AlreadyListenedAbooks.index(string4add)
#						print(self.AlreadyListenedAbooks[index])

			page += 1
			ProcessBooks += BooksPerPage
			if ProcessBooks >= AllBooks:
				break

	def AddAbookToAlreadyListenedList(self, abook_path):
		time.sleep(0.5)
		html = self.session.get(globalData.HOST + abook_path)

#		FindList = codecs.open('BookPage.html', 'w', 'utf-8-sig')
#		FindList.write(html.text)
#		FindList.close()

		mainPagesoup = BeautifulSoup(html.text, 'html.parser')

		BookNameTag = mainPagesoup.find('div', class_='book_header_name')
		if BookNameTag:
			BookName = BookNameTag.text.strip()

		BookReaderBlockTag = mainPagesoup.find('div', class_='book_info_line icon_reader clearfix')
		if BookReaderBlockTag:
			BookReaderTag = BookReaderBlockTag.find('a', class_='book_info_line_link with_icon')
			if BookReaderTag:
				BookReader = BookReaderTag.text.strip()
			else:
				BookReaderTag = BookReaderBlockTag.find('a', class_='book_info_line_link')
				if BookReaderTag:
					BookReader = BookReaderTag.text.strip()

		string4add = BookName + ':' + BookReader
		if self.AlreadyListenedAbooks.count(string4add) == 0:
			self.AlreadyListenedAbooks.append(
				string4add)  # После успешной обработки пользователя добавляем его в игнор для более быстрой обработки в будущем


	def AddShelfListToAlreadyListenedList(self, abook_list):
			for abook in abook_list:
				abook_split = abook.split(':')
				self.AddAbookToAlreadyListenedList(abook_split[1])


	def __init__(self, session):
		self.session = session
		self.ErrCodeVal = 0
		self.FindAlreadyListenedProcess()

if __name__ == '__main__':
	login = loginClass()
	if login.Result:

		makelist = makeAlreadyListenedList(login.session)
		makelist.AddAbookToAlreadyListenedList('/book/stukach-2/')
#		print(makelist.AlreadyListenedAbooks)