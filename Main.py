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
from shelf import Shelf
from GlobalData import globalData
from makealreadylistenedlist import makeAlreadyListenedList
from FindBooksMakeList import findBooksMakeList
from DownloadAudiobooks import downloadAudiobooks


def GetCurrentTime():
	now = datetime.now()
	return(int(now.day),int(now.hour),int(now.minute))

def MainProcess():
#1.Логинимся
	login = loginClass()
	if login.Result:
#Инициализируем объекты:
		download = downloadAudiobooks(login.session)
#2.Получаем список уже прослушанных книг с сайта
		make_skip_list = makeAlreadyListenedList(login.session)
#3.Обрабатываем список книг на "полке": составляем список книг с прогрессом прослушивания 100%,
#удаляем их с "полки" по списку
		shelf = Shelf(login.session, login.globaltoken)
		shelf.MakeListABooksOnShelf()
		shelf.UnFaveCompletedAbooksFromShelf()
#4.Получаем оставшееся количество книг на "полке",получаем разницу с заданным числом,
#например, 20: 20-15 = 5
		nAbookRequired = globalData.MAX_BOOKS_ON_SHELF - shelf.GetnBooksOnShelf()
#5. Находим 5 книг по заданным критериям(жанр,рейтинг,новизне книги) и добавляем
#на "полку".Добавляем их также в "слушаемые"(посылаем запрос play)
		if nAbookRequired > 0:
			makeFindList = findBooksMakeList(login.session, nAbookRequired, make_skip_list.AlreadyListenedAbooks,
											use_time_filter=globalData.IS_USE_TIME_LIMIT_FOR_SHELF,
										time_duration_in_min_from=globalData.TIME_FROM_SHELF_IN_MIN, time_duration_in_min_to=globalData.TIME_TO_SHELF_IN_MIN)
			makeFindList.makeList()
			shelf.FaveAbooksByList(makeFindList.FindBooksList)
			make_skip_list.AddShelfListToAlreadyListenedList(makeFindList.FindBooksList)
			download.SendPlayAbookList(makeFindList.FindBooksList)
#6.Обрабатываем каталог со скачанными книгами.Подсчитываем количество вложенных каталогов-
#названий книг.Находим разницу с заданным числом,например, 20: 20-11 = 9
		nAbookDownloadRequired = globalData.MAX_DOWNLOADED_BOOKS - download.getnAbooksInDir()
		if nAbookDownloadRequired > 0:
#7. Находим 9 книг по заданным критериям(жанр,рейтинг,новизне книги и ограничения по времени
#звучания) и скачиваем книги в папку  скачанных книг.Добавляем их также в "слушаемые"
#(посылаем запрос play)
			makeFindList = findBooksMakeList(login.session, nAbookDownloadRequired, make_skip_list.AlreadyListenedAbooks,
											use_time_filter=globalData.IS_USE_TIME_LIMIT_FOR_DOWNLOAD,
											time_duration_in_min_from=globalData.TIME_FROM_DOWNLOAD_IN_MIN,
											time_duration_in_min_to=globalData.TIME_TO_DOWNLOAD_IN_MIN)
			makeFindList.makeList()
			download.DownloadAbookList(makeFindList.FindBooksList)
#8.В случае успешной отработки  переносим следующую активацию на сутки.
		print('OK')
		return True
	else:
		print('Error occurred')
		return False



today = 0

if __name__ == '__main__':
#	MainProcess()
	while True:
		day, hour, minute = GetCurrentTime()
		if day != today:
			if hour == globalData.HOUR_START and minute >= globalData.MINUTE_START:
				if MainProcess() == True:
					today = day
		time.sleep(30)



