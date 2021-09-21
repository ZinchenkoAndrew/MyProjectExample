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
from GlobalData import globalData
from login import loginClass
from makealreadylistenedlist import makeAlreadyListenedList

class findBooksMakeList():
	def __init__(self, session, books_required, AlreadyListenedAbooks, use_time_filter=False, time_duration_in_min_from=30, time_duration_in_min_to=180):
		self.use_time_filter = use_time_filter
		self.time_duration_in_min_from = time_duration_in_min_from
		self.time_duration_in_min_to = time_duration_in_min_to
		self.books_required = books_required
		self.AlreadyListenedAbooks = AlreadyListenedAbooks
		self.session = session
		self.FindBooksList = []
	#globalData.link2FindBooksPage = '/genre/uzhasy-mistika/rating' #сортировка: по рейтингу
	def makeList(self):
		page = 1
		AllBooks = 0
		ProcessBooks = 0
		current_find_books = 0
		self.FindBooksList.clear()
		print('\r\n************Поиск новых книг:**************')
		while (1):
	#		FindUrl = globalData.HOST + globalData.link2FindBooksPage+'/?page='+str(page)
			FindUrl = globalData.HOST + globalData.link2FindBooksPage+'/'+str(page)+'/?period=alltime'
#			print(FindUrl)
			time.sleep(0.5)
			html = self.session.get(FindUrl)

			if html.status_code == 200:
#				FindList = codecs.open('FavoritesResultFind.html','w','utf-8-sig')
#				FindList.write(html.text)
#				FindList.close()
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
					nBooksTag = FindListsoup.find('div', class_='genre_header_info_text')
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
					booknametag = li.find('a', class_='bookitem_name')
					if booknametag is None:
						continue
					reader = li.find('div', class_='bookitem_meta_block icon_reader')
					if reader is None:
						continue
					author = li.find('div', class_='bookitem_meta_block icon_author')

					timetag = li.find('div', class_='bookitem_meta_block icon_time')
					if timetag is None:
						continue
					TimeStr = timetag.find('div', class_='bookitem_meta_block_content').text
					hoursList = re.findall(r'\d+ час',TimeStr)
					minutesList = re.findall(r'\d+ мин', TimeStr)
					if self.use_time_filter:
						hours = 0
						if len(hoursList) > 0:
							hours = int(re.findall(r'\d+',hoursList[0])[0])
						minutes = int(re.findall(r'\d+', minutesList[0])[0])
						minutes += hours * 60
						if minutes < self.time_duration_in_min_from or minutes > self.time_duration_in_min_to:
							continue
					NameOfReader = reader.find('a', class_='bookitem_meta_link').text
					NameOfAuthor = 'Unknown' if author is None else author.find('a', class_='bookitem_meta_link').text
					NameOfBook = booknametag.text.strip()

					#Фильтр по присутствию в названии книги заданных слов:
					is_skip_by_word = False
					for black_word in globalData.BLACK_LIST_OF_NAME_WORDS:
						black_word_lower = black_word.lower()
						NameOfBook_lower = NameOfBook.lower()
						if NameOfBook_lower.find(black_word_lower) >= 0:
							is_skip_by_word = True
							break
					if is_skip_by_word == True:
						continue
#					print('Abook: ' + NameOfBook + '   reader: ' + NameOfReader)


					#Фильтр по чтецам и авторам книг:
					if globalData.BLACK_LIST_OF_READERS.count(NameOfReader) > 0:
						continue
					if globalData.BLACK_LIST_OF_AUTHORS.count(NameOfAuthor) > 0:
						continue
					string4add = NameOfBook + ':' + NameOfReader

					locallinkBook = booknametag.get('href')

#					print('link to Abook: ' +globalData.HOST + locallinkBook)

					#Пропускаем книги из списка уже слушаемых,если книга новая,то:
					if self.AlreadyListenedAbooks.count(string4add) == 0:
						#Заходим на страницу книги:
						time.sleep(0.5)
						html = self.session.get(globalData.HOST + locallinkBook)
						RefererLink = globalData.HOST + locallinkBook

#						FindList = codecs.open('BookPage.html','w','utf-8-sig')
#						FindList.write(html.text)
#						FindList.close()
						mainPagesoup = BeautifulSoup(html.text, 'html.parser')
#Если книга платная,то пропускаем:
						btn = mainPagesoup.find('div', class_='book_buy_wrap')
						if btn:
#							print('Книга платная')
							continue
#Если автор заблокировал книгу,то пропускаем:
						block = mainPagesoup.find('div', class_='book_blocked_block')
						if block:
#							print('Доступ ограничен по просьбе автора.')
							continue

						mainPagesoupStr = html.text
						LikesStringIndexStart = mainPagesoupStr.find('"likesCount"')
						LikesStringIndexStop = mainPagesoupStr.find('<',LikesStringIndexStart)
						LikesString = mainPagesoupStr[LikesStringIndexStart:LikesStringIndexStop]
						nLikes = int(re.findall(r'\d+',LikesString)[0])

						disLikesStringIndexStart = mainPagesoupStr.find('"dislikesCount"')
						disLikesStringIndexStop = mainPagesoupStr.find('<', disLikesStringIndexStart)
						disLikesString = mainPagesoupStr[disLikesStringIndexStart:disLikesStringIndexStop]
						ndisLikes = int(re.findall(r'\d+', disLikesString)[0])

						if ndisLikes == 0:
							ndisLikes += 1
							nLikes += 1
						if nLikes >= 10:
							if nLikes/ndisLikes < 2:
								continue


						BookControllerIndex = mainPagesoupStr.find('BookController.enter')
						if (BookControllerIndex < 0):
							print("Can't BookController.enter in book:"+string4add)
							continue

						StartJSONIndex = mainPagesoupStr.find('(', BookControllerIndex) + 1
						StopJSONIndex = mainPagesoupStr.find(');', StartJSONIndex)
						JsonData = mainPagesoupStr[StartJSONIndex:StopJSONIndex]

#						print(JsonData)

						dict = json.loads(JsonData)
						id = dict['id']

						self.FindBooksList.append(str(id) + ':'+locallinkBook)
						print('Найдена новая книга: ' + string4add)
						current_find_books += 1
						if current_find_books >= self.books_required:
							return


			page += 1
			ProcessBooks += BooksPerPage
			if ProcessBooks >= AllBooks:
				break

if __name__ == '__main__':
	login = loginClass()
	if login.Result:
		makeBlackList = makeAlreadyListenedList(login.session)
		makeFindList = findBooksMakeList(login.session, 20, makeBlackList.AlreadyListenedAbooks, use_time_filter=False, time_duration_in_min_from=30, time_duration_in_min_to=180)
		makeFindList.makeList()
		print(makeFindList.FindBooksList)
