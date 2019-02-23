import urllib.parse

import requests
from bs4 import BeautifulSoup
from emoji import emojize
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bot import log
from bot_files.utils import prepare_next_items
from const import FLIBUSTA_TEMPLATE, FLIB_END


def flibusta_search(query):
    query_param = urllib.parse.quote_plus("название:(%s)" % query, encoding='utf-8')
    response = requests.get(FLIBUSTA_TEMPLATE % query_param + FLIB_END)
    body = BeautifulSoup(response.content, "lxml")

    found_books = body.findAll('div', {'class': 'col-sm-12 serp-row'})

    result_books = []
    for book in found_books:
        title = book.find('h3', {'class': 'title'}).a
        author = title.next.next.next.next
        try:
            href = book.find('a', {'class': "search-type away"}).attrs['href'].split('=')[1]
        except AttributeError:
            continue
        result_books += [{
            'author': author.text,
            'title': title.text,
            'href': href,
        }]
    return result_books


def show_flibusta_book(bot, update, user_data):
    for i, r_book in enumerate(user_data['found_books'][:5]):
        user_data['FLIBUSTA_BOOKS'][i + 1] = r_book['href']
        reply = "%d. \"%s\" by %s" % (i + 1, r_book['title'], r_book['author'])
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply)


def flibusta_book(bot, update, user_data):
    log.log_user(update)
    try:
        answer = int(update.message.text)
        reply = "Держи ссылку!\n %s" % (user_data['FLIBUSTA_BOOKS'][answer])
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply, reply_markup=ReplyKeyboardRemove())
        reply = emojize('Приятного чтения! \n:heart: :book:', use_aliases=True)
        log.log_bot(reply, update)
        update.message.reply_text(reply)
    except KeyError:
        reply = "Упс, что-то не так, попробуйте снова"
        log.log_bot(reply, update)
        bot.send_message(chat_id=update.message.chat_id, text=reply, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def flibusta(bot, update, args, user_data):
    log.log_user(update)
    if args:
        found_books = flibusta_search(' '.join(args))
        if not found_books:
            reply = "Ничего не найдено!"
            log.log_bot(reply, update)
            update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        user_data['found_books'] = found_books
        user_data['FLIBUSTA_BOOKS'] = {}

    if update.message.text == 'Дальше!' or args:
        show_flibusta_book(bot, update, user_data)
        reply_keyboard = prepare_next_items(user_data, 'found_books')

        reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_rows=2,
                                           one_time_keyboard=True,
                                           resize_keyboard=True)
        reply = "Выбери номер книги внизу"
        log.log_bot(reply, update)
        update.message.reply_text(reply, reply_markup=reply_markup)
        return 12
    else:
        reply = "Введи запрос!"
        log.log_bot(reply, update)
        update.message.reply_text(reply)
