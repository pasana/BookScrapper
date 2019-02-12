import os

bot_token = os.environ['TELEGRAM_TOKEN']

import urllib.parse
import tempfile

import requests
from bs4 import BeautifulSoup
from emoji import emojize
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from const import SEARCH_TEMPLATE
from parser import Parser

from bot import log
from bot_files.utils import prepare_next_books


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
        except ValueError:
            reply = 'Что-то не так с идентификатором книги... Попробуй еще раз!'
            log.log_bot(reply, update)
            update.message.reply_text(reply)
            return ConversationHandler.END
        bot.send_document(chat_id=update.message.chat_id,
                          document=file_result,
                          # TODO: filename checker
                          filename=tempfile.NamedTemporaryFile().name + ".fb2")
        reply = emojize('Приятного чтения! \n:heart: :book:', use_aliases=True)
        log.log_bot(reply, update)
        update.message.reply_text(reply)
        return ConversationHandler.END


def author(bot, update, args=None, user_data=None):
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
    if args or 'AUTHORS' in keys:
        try:
            if args:
                id = int(args[0])
                parser = Parser(id)
            elif 'AUTHORS' in keys:
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

                if update.message.text == 'Дальше!' or 'BOOKS' in user_data.keys():
                    show_found_books(bot, update, user_data, author=author_id)
                    reply_keyboard = prepare_next_books(user_data)

                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                                       one_time_keyboard=True,
                                                       resize_keyboard=True)
                    reply = "Выбери номер книги внизу"
                    log.log_bot(reply, update)
                    update.message.reply_text(reply, reply_markup=reply_markup)
                    return 12

        except ValueError:
            reply = 'Что-то не так с идентификатором... Попробуй еще раз!'
            log.log_bot(reply, update)
            update.message.reply_text(reply)
            return
        return ConversationHandler.END


def loveread_search(args):
    query = ' '.join(args)
    query_param = urllib.parse.quote_plus(query, encoding='cp1251')
    response = requests.get(SEARCH_TEMPLATE % query_param)
    body = BeautifulSoup(response.content, "lxml")
    try:
        found_books = body.find('div', {'class': "contents"}).parent.parent.findAll('li')[1:]
    except AttributeError:
        return None
    return found_books


def show_found_authors(bot, update, user_data, index_start=0):
    for i, r_book in enumerate(user_data['found_books'][:5]):
        author = r_book.a.text.strip()
        author_id = r_book.a.attrs['href'].split('?')[1].split('=')[1]
        user_data['AUTHORS'][i + 1] = author_id
        reply = "%d. by %s" % (i + 1, author)
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply)


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


# TODO: reorganize into book, author, series and split
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

        reply_keyboard = prepare_next_books(user_data)

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
