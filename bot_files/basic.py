import os

bot_token = os.environ['TELEGRAM_TOKEN']

from emoji import emojize
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bot import log


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
