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
from login import loginClass
from GlobalData import globalData


class Shelf():
	def __init__(self, session, globaltoken):
		self.nBooksOnShelf = 0
		self.AbooksOnShelf = []
		self.session = session
		self.globaltoken = globaltoken
#		self.FindBooksOnShelfProcess()
#		self.UnfaveBooksCompleted()
#		self.GetnBooksOnShelf()

	def GetnBooksOnShelf(self):

		self.nBooksOnShelf = 0
		page = 1
		FindUrl = globalData.HOST + globalData.link2AbooksOnShelfPage + '?page=' + str(page)
		time.sleep(0.5)
		html = self.session.get(FindUrl)

		if html.status_code == 200:
			#			FindList = codecs.open('AbooksOnShelfResultFind.html','w','utf-8-sig')
			#			FindList.write(html.text)
			#			FindList.close()
			FindListsoup = BeautifulSoup(html.text, 'html.parser')

			nBooksTag = FindListsoup.find('div', class_='user_shelf_books_count')
			if nBooksTag is None:
				self.ErrCodeVal = 1
				return
			nBooksStr = nBooksTag.text
			try:
				self.nBooksOnShelf = int((re.findall(r'\d+', nBooksStr)[0]))
			except Exception as e:
				print('Error occerred {0}'.format(e))
				self.nBooksOnShelf = 0
			print('Всего книг на полке:'+str(self.nBooksOnShelf))
			return self.nBooksOnShelf

	def UnFaveAbook(self, bookId):
		time.sleep(0.5)
		linkToUnfave = '/ajax/book/' + str(bookId) + '/unfave/'
		html = self.session.post(globalData.HOST + linkToUnfave, data={'token': self.globaltoken})
#		print(html.text)

	def FaveAbook(self, bookId):
		time.sleep(0.5)
		linkTofave = '/ajax/book/' + str(bookId) + '/fave/'
		html = self.session.post(globalData.HOST + linkTofave, data={'token': self.globaltoken})
#		print(html.text)

	def UnfaveAllShelf(self):
		print('Удаление всех книг с полки... ')

		for abook in self.AbooksOnShelf:
			abook_split = abook.split(':')
			bookId = abook_split[0]
			self.UnFaveAbook(bookId)
			print('Удалена с полки книга: ' + abook)

	def UnFaveCompletedAbooksFromShelf(self):

		self.ErrCodeVal = 0

		print('Удаление с полки завершенных книг... ')

		for abook in self.AbooksOnShelf:

			abook_split = abook.split(':')
			bookId = abook_split[0]
			locallinkBook = abook_split[1]

			print('link: ' + globalData.HOST + locallinkBook)

			time.sleep(0.5)
			html = self.session.get(globalData.HOST + locallinkBook)

#					FindList = codecs.open('BookPage.html', 'w', 'utf-8-sig')
#					FindList.write(html.text)
#					FindList.close()
			mainPagesoup = BeautifulSoup(html.text, 'html.parser')

			mainPagesoupStr = html.text
			if mainPagesoupStr.find('book_small_player_time__progress -completed') >= 0:
				self.UnFaveAbook(bookId)
				print('Удалена с полки книга: ' + abook)



	def MakeListABooksOnShelf(self):

		self.AbooksOnShelf.clear()

		self.ErrCodeVal = 0

		print('Создание списка книг на полке')

		page = 1
		AllBooks = 0
		ProcessBooks = 0
		while (1):

			FindUrl = globalData.HOST + globalData.link2AbooksOnShelfPage + '?page='+str(page)
			print(FindUrl)
			time.sleep(0.5)
			html = self.session.get(FindUrl)

			if html.status_code == 200:
	#			FindList = codecs.open('AbooksOnShelfResultFind.html','w','utf-8-sig')
	#			FindList.write(html.text)
	#			FindList.close()
				FindListsoup = BeautifulSoup(html.text, 'html.parser')
				if FindListsoup is None:
					self.ErrCodeVal = 1
					break
				liList = FindListsoup.find_all('span', class_='bookitem')
	#			print('liList='+str(liList))

				if liList is None or len(liList) == 0:
					self.ErrCodeVal = 2
					break

				if page == 1:
					nBooksTag = FindListsoup.find('div',class_='user_shelf_books_count')
					if nBooksTag is None:
						self.ErrCodeVal = 3
						break
					nBooksStr = nBooksTag.text.replace(' ', '')
					AllBooks = int(re.findall(r'\d+', nBooksStr)[0])
				#Список ссылок на книги на полке
				BooksPerPage = len(liList)
#				print(
#					'books ' + str(ProcessBooks+1) + '...' + str(ProcessBooks + BooksPerPage ) + '---------------------------------')
				for li in liList:
					bookIdStr = li.get('id')
					bookId = re.findall(r'\d+',bookIdStr)[0]
					booknametag = li.find('a',class_='bookitem_name')
					reader = li.find('div',class_='bookitem_meta_block icon_reader')
					NameOfReader = reader.find('a',class_='bookitem_meta_link').text
					NameOfBook = booknametag.text.strip()

					print('Книга на полке: ' + NameOfBook + ' читает: ' + NameOfReader)


					locallinkBook = booknametag.get('href')

					print('Ссылка: ' + globalData.HOST + locallinkBook)

					self.AbooksOnShelf.append(bookId + ':' + locallinkBook)
			page += 1
			ProcessBooks += BooksPerPage
			if ProcessBooks >= AllBooks:
				break

		return self.ErrCodeVal == 0

	def SaveAbooksOnShelfListToFile(self, filename):
		f = open(filename, 'w', encoding='utf-8')
		for abook in self.AbooksOnShelf:
			f.write(abook + '\r\n')
		f.close()

	def LoadAbooksOnShelfListFromFile(self, filename):
		self.AbooksOnShelf.clear()
		with open(filename, 'r', encoding='utf-8') as f:
			for row in f:
				line = row.replace('\n', '')
				if len(line) == 0:
					continue
				self.AbooksOnShelf.append(line)
		f.close()

	def FaveAbooksByList(self, list_of_abooks):
		print('Fave all Abooks... ')

		for abook in list_of_abooks:
			abook_split = abook.split(':')
			bookId = abook_split[0]
			self.FaveAbook(bookId)
#			print('Fave abook: ' + abook)


if __name__ == '__main__':
	login = loginClass()
	if login.Result:
		shelf = Shelf(login.session, login.globaltoken)
#		shelf.GetnBooksOnShelf()
		shelf.MakeListABooksOnShelf()
#		print(shelf.AbooksOnShelf)
#		shelf.UnFaveCompletedAbooksFromShelf()
		shelf.SaveAbooksOnShelfListToFile('shelf.txt')
#		shelf.UnfaveAllShelf()
#		shelf.LoadAbooksOnShelfListFromFile('shelf.txt')
#		shelf.FaveAbooksByList(shelf.AbooksOnShelf)
	else:
		print('Error occurred')


