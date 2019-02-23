import os

bot_token = os.environ['TELEGRAM_TOKEN']

import urllib.parse

import requests
from bs4 import BeautifulSoup
from emoji import emojize
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from const import SEARCH_TEMPLATE
from parser import Parser

from bot import log
from bot_files.utils import prepare_next_items, valid_filename


def book(bot, update, args=None, user_data=None):
    log.log_user(update)
    if args:
        if len(args) > 1:
            reply = "Это должно быть одно число!"
            log.log_bot(reply, update)
            update.message.reply_text(reply)
    try:
        keys = user_data.keys()
    except:
        keys = []
    if args or 'BOOK' in keys or 'BOOKS' in keys:
        try:
            if args:
                id = int(args[0])
                parser = Parser(id)
            elif 'BOOK' in keys:
                parser = user_data['BOOK']
                del user_data['BOOK']
            elif 'BOOKS' in keys:
                parser = Parser(int(user_data['BOOKS'][int(update.message.text)]))
                del user_data['BOOKS']

            reply = emojize(
                "Скачиваю \"%s\" by %s для тебя! :sparkles: \nОставайся на связи! :hourglass:" % (parser.book_name,
                                                                                                  parser.author),
                use_aliases=True)
            log.log_bot(reply, update)
            bot.send_message(chat_id=update.message.chat_id,
                             text=reply,
                             reply_markup=ReplyKeyboardRemove())

            filename = parser.run()
            file_result = parser.doc.get_file()
            bot.send_document(chat_id=update.message.chat_id,
                              document=file_result,
                              filename=valid_filename(filename)
                              # filename=tempfile.NamedTemporaryFile().name + ".fb2"
                              )
            reply = emojize('Приятного чтения! \n:heart: :book:', use_aliases=True)
            log.log_bot(reply, update)
            update.message.reply_text(reply)
            return ConversationHandler.END
        except ValueError:
            reply = 'Что-то не так с идентификатором книги... Попробуй еще раз!'
            log.log_bot(reply, update)
            update.message.reply_text(reply)
            return ConversationHandler.END
    return ConversationHandler.END


def author(bot, update, args=None, user_data=None):
    log.log_user(update)
    try:
        keys = user_data.keys()
    except:
        keys = []
    if 'AUTHORS' in keys:
        try:
            author_id = user_data['AUTHORS'][int(update.message.text)]
            del user_data['AUTHORS']
            response = requests.get('http://loveread.ec/biography-author.php?author=%s' %
                                    author_id)
            body = BeautifulSoup(response.content, "lxml")
            try:
                user_data['found_books'] = body.find('ul', {'class': "sr_book"}).findAll('li')[1:]
                user_data['BOOKS'] = {}
            except AttributeError:
                pass
            author_name = body.find('h2').text
            display_books(bot, update, args, user_data, author=author_name)
            return 21
        except ValueError:
            reply = 'Что-то не так с идентификатором... Попробуй еще раз!'
            log.log_bot(reply, update)
            update.message.reply_text(reply)
            return ConversationHandler.END


# TODO: series
def series(bot, update, args=None, user_data=None):
    pass

def loveread_search(args):
    query = ' '.join(args)
    query_param = urllib.parse.quote_plus(query, encoding='cp1251')
    response = requests.get(SEARCH_TEMPLATE % query_param)
    body = BeautifulSoup(response.content, "lxml")
    try:
        contents = body.findAll('div', {'class': "contents"})
        found_books, found_authors, found_series = None, None, None
        for content in contents:
            if content.text == 'Найденные книги:':
                found_books = content.parent.parent.findAll('li')[1:]
            if content.text == 'Найденные авторы:':
                found_authors = content.parent.parent.findAll('li')[1:]
            if content.text == 'Найденные серии:':
                found_series = content.parent.parent.findAll('li')[1:]
    except AttributeError:
        return None
    return found_books, found_authors, found_series


def show_found_books(bot, update, user_data, index_start=0, author=None):
    for i, r_book in enumerate(user_data['found_books'][:5]):
        if author:
            title = r_book.findAll('a')[0].text.strip()
        else:
            title, author = list(map(lambda x: x.text.strip(), r_book.findAll('a')))
        book_id = r_book.a.attrs['href'].split('?')[1].split('=')[1]
        user_data['BOOKS'][i + 1] = book_id
        reply = "%d. \"%s\" by %s" % (i + 1, title, author)
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def show_found_authors(bot, update, user_data, index_start=0):
    for i, r_book in enumerate(user_data['found_authors'][:5]):
        author = r_book.a.text.strip()
        author_id = r_book.a.attrs['href'].split('?')[1].split('=')[1]
        user_data['AUTHORS'][i + 1] = author_id
        reply = "%d. %s" % (i + 1, author)
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def show_found_series(bot, update, user_data, index_start=0):
    for i, r_book in enumerate(user_data['found_series'][:5]):
        series_name = r_book.a.text.strip()
        series_id = r_book.a.attrs['href'].split('?')[1].split('=')[1]
        user_data['SERIES'][i + 1] = series_id
        reply = "%d. %s" % (i + 1, series_name)
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def display_books(bot, update, args=None, user_data=None, author=None):
    if update.message.text == 'Дальше!' or user_data['found_books']:
        show_found_books(bot, update, user_data, author=author)
        reply_keyboard = prepare_next_items(user_data, 'found_books')

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        reply = "Выбери номер книги внизу"
        log.log_bot(reply, update)
        update.message.reply_text(reply, reply_markup=reply_markup)
        return 21
    return ConversationHandler.END


def display_authors(bot, update, args=None, user_data=None):
    if update.message.text == 'Дальше!' or user_data['found_authors']:
        show_found_authors(bot, update, user_data)
        reply_keyboard = prepare_next_items(user_data, 'found_authors')

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        reply = "Выбери номер автора внизу"
        log.log_bot(reply, update)
        update.message.reply_text(reply, reply_markup=reply_markup)
        return 22
    return ConversationHandler.END


def display_series(bot, update, args=None, user_data=None):
    if update.message.text == 'Дальше!' or user_data['found_series']:
        show_found_series(bot, update, user_data)
        reply_keyboard = prepare_next_items(user_data, 'found_series')

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        reply = "Выбери номер автора внизу"
        log.log_bot(reply, update)
        update.message.reply_text(reply, reply_markup=reply_markup)
        return 23
    return ConversationHandler.END


def find(bot, update, args=None, user_data=None):
    log.log_user(update)
    if args:
        books, authors, series = loveread_search(args)
        if not (books or authors or series):
            reply = "Ничего не найдено!"
            log.log_bot(reply, update)
            update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        reply_keyboard = []
        if books:
            user_data['found_books'] = books
            user_data['BOOKS'] = {}
            reply_keyboard += [['Книги']]
        if authors:
            user_data['found_authors'] = authors
            user_data['AUTHORS'] = {}
            reply_keyboard += [['Авторы']]
        # if series:
        #     user_data['found_series'] = series
        #     user_data['SERIES'] = {}
        #     reply_keyboard += [['Серии книг']]
        if len(reply_keyboard) == 1:
            if books:
                display_books(bot, update, args, user_data)
                return 21
            if authors:
                display_authors(bot, update, args, user_data)
                return 22
        reply_keyboard += [['Отмена']]

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        reply = "Что тебя интересует?"
        log.log_bot(reply, update)
        update.message.reply_text(reply, reply_markup=reply_markup)
        return 12

    else:
        reply = "Введи запрос!"
        log.log_bot(reply, update)
        update.message.reply_text(reply)


# TODO: replace by find in other modules
def find_book(bot, update, args=None, user_data=None):
    log.log_user(update)
    book_flag = 0
    author_flag = 0
    if args:
        found_books = loveread_search(args)
        if not found_books:
            reply = "Ничего не найдено!"
            log.log_bot(reply, update)
            update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        classes = set(map(lambda x: x.a.attrs['class'][0], found_books))
        if classes == {'letter_author'}:
            author_flag = 1
        else:
            book_flag = 1
        if book_flag:
            user_data['found_books'] = found_books
            user_data['BOOKS'] = {}
        if author_flag:
            user_data['found_books'] = found_books
            user_data['AUTHORS'] = {}

    if update.message.text == 'Дальше!' or args:
        if book_flag:
            show_found_books(bot, update, user_data)
        if author_flag:
            show_found_authors(bot, update, user_data)

        reply_keyboard = prepare_next_items(user_data, 'found_books')

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        reply = "Выбери номер книги внизу"
        log.log_bot(reply, update)
        update.message.reply_text(reply, reply_markup=reply_markup)
        if book_flag:
            return 12
        if author_flag:
            return 13
        return 12
    else:
        reply = "Введи запрос!"
        log.log_bot(reply, update)
        update.message.reply_text(reply)
