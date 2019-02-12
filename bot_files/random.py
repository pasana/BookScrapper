import random

from telegram import ReplyKeyboardMarkup

from bot import log
from parser import Parser


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
