import os

bot_token = os.environ['TELEGRAM_TOKEN']

import random
import urllib.parse
import tempfile

import requests
from bs4 import BeautifulSoup
from emoji import emojize
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

from const import SEARCH_TEMPLATE, FLIBUSTA_TEMPLATE, FLIB_END
from parser import Parser
from logger import Logger

# logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

log = Logger()


def start(bot, update):
    log.log_user(update)
    reply = emojize("Привет! :v: \n\nЯ бот, который поможет тебе получить любую книгу "
                    "с сайта LoveRead.ec в формате FB2. :books: \n\nДля этого используй команду "
                    "/book с идентификатором книги. Например, /book 2039\n\n"
                    "Также ты можешь положиться на волю случая и воспользоваться командой /random\n\n"
                    "Или найти по ключевым словам с помощью /find или /flibusta. Например, /find система"
                    "\n\nПодписывайся на новости! https://t.me/book_scrapper",
                    use_aliases=True)
    log.log_bot(reply, update)
    bot.send_message(chat_id=update.message.chat_id, text=reply)


def hello(bot, update):
    log.log_user(update)
    reply = emojize('Привет, {}! :v:'.format(update.message.from_user.first_name), use_aliases=True)
    log.log_bot(reply, update)
    update.message.reply_text(reply)


def unknown(bot, update):
    log.log_user(update)
    reply = emojize("А разве такая команда существует? :hushed:", use_aliases=True)
    log.log_bot(reply, update)
    bot.send_message(chat_id=update.message.chat_id, text=reply)


def unknown_text(bot, update):
    log.log_user(update)
    reply = emojize(":hushed:", use_aliases=True)
    log.log_bot(reply, update)
    bot.send_message(chat_id=update.message.chat_id, text=reply)


def cancel(bot, update, user_data):
    try:
        for key in user_data.keys():
            del user_data[key]
    except:
        pass

    log.log_user(update)
    reply = "Ладненько"
    log.log_bot(reply, update)
    update.message.reply_text(reply, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


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


def init_random_book():
    id = random.randint(1, 100000)
    try:
        parser = Parser(id)
    except AttributeError:
        return None
    return parser


def random_book(bot, update, user_data):
    log.log_user(update)
    parser = None
    while parser is None:
        parser = init_random_book()
    user_data['BOOK'] = parser

    reply = "\"%s\" by %s." % (parser.book_name, parser.author)
    log.log_bot(reply, update)
    bot.send_message(chat_id=update.message.chat_id, text=reply)

    reply_keyboard = [["Да!", "Нет", "Давай другую!"]]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, n_cols=2,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    reply = "Ну что, читаем?"
    log.log_bot(reply, update)
    update.message.reply_text(reply, reply_markup=reply_markup)
    return 11


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


def prepare_next_books(user_data):
    if len(user_data['found_books']) > 5:
        user_data['found_books'] = user_data['found_books'][5:]
        reply_keyboard = [[str(x) for x in range(1, 6)], ["Отмена", "Дальше!"]]
    else:
        reply_keyboard = [[str(x) for x in range(1, len(user_data['found_books']) + 1)], ["Отмена"]]
        del user_data['found_books']
    return reply_keyboard


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
        reply_keyboard = prepare_next_books(user_data)

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


def main():
    updater = Updater(bot_token)
    dp = updater.dispatcher

    random_handler = ConversationHandler(
        entry_points=[CommandHandler('random', random_book, pass_user_data=True)],
        states={

            11: [RegexHandler('Да!', book, pass_user_data=True),
                 RegexHandler('Нет', cancel, pass_user_data=True),
                 RegexHandler('Давай другую!', random_book, pass_user_data=True)
                 ]
        },
        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)], allow_reentry=True
    )

    find_handler = ConversationHandler(
        entry_points=[CommandHandler('find', find_book, pass_args=True, pass_user_data=True)],
        states={

            12: [RegexHandler('\d', book, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', find_book, pass_user_data=True)
                 ],
            13: [RegexHandler('\d', author, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', find_book, pass_user_data=True)
                 ]

        },
        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)], allow_reentry=True
    )

    flibusta_handler = ConversationHandler(
        entry_points=[CommandHandler('flibusta', flibusta, pass_args=True, pass_user_data=True)],
        states={

            12: [RegexHandler('\d', flibusta_book, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', flibusta, pass_user_data=True)
                 ]
        },
        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)], allow_reentry=True
    )

    dp.add_handler(CommandHandler('hello', hello))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('book', book, pass_args=True))
    dp.add_handler(random_handler)
    dp.add_handler(find_handler)
    dp.add_handler(flibusta_handler)
    dp.add_handler(MessageHandler(Filters.command, unknown))
    # dp.add_handler(MessageHandler(Filters.text, unknown_text))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
