class globalData():
    HOUR_START = 3 #Стартовать скрипт в ... часов
    MINUTE_START = 0 #Стартовать скрипт в ... минут

    IS_USE_TIME_LIMIT_FOR_SHELF = True #Разрешить использовать фильтр - лимит книг по времени для книжной полки
    TIME_FROM_SHELF_IN_MIN = 15 #Искать и класть книги на полку,только если они длятся ОТ ... минут
    TIME_TO_SHELF_IN_MIN = 240 #Искать и класть книги на полку,только если они длятся ДО ... минут

    IS_USE_TIME_LIMIT_FOR_DOWNLOAD = True #Разрешить использовать фильтр - лимит книг по времени для скачиваемых книг
    TIME_FROM_DOWNLOAD_IN_MIN = 30  # Искать и скачивать книги в папку только, если они длятся ОТ ... минут
    TIME_TO_DOWNLOAD_IN_MIN = 90  # Искать и скачивать книги в папку только, если они длятся ДО ... минут

    HOST = 'https://m.knigavuhe.org'
    MP3_DIR = 'audiobooks_origin_volume' #Папка для скачанных аудиокниг
    MAX_BOOKS_ON_SHELF = 27 #Максимальное число книг на полке
    MAX_DOWNLOADED_BOOKS = 26 #Максимальное число книг в папке для скачивания
    BLACK_LIST_OF_NAME_WORDS = ['Якутия']# Пропустить, если в названии книги встречаются перечисленные слова
    BLACK_LIST_OF_AUTHORS = ['Говард Филлипс Лавкрафт', 'Стивен Кинг']# Черный список авторов
    BLACK_LIST_OF_READERS = ['Владимир Князев']  # Черный список исполнителей
    link2FindBooksPage = '/genre/uzhasy-mistika/rating'  # Линк для поиска книг в жанре ужасы/мистика ,сортировка по рейтингу
    link2AlreadyListenedPage = '/user170572/played' #Линк на слушаемые книги
    link2AbooksOnShelfPage = '/shelf/' #Линк на книжную "полку"(Избранное)
