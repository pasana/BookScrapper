import os

bot_token = os.environ['TELEGRAM_TOKEN']

from emoji import emojize
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from bot import log
from bot_files.find import find
from bot_files.flibusta import flibusta


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


# TODO: should be replaced by ForceReply
# https://stackoverflow.com/questions/44639923/telegram-bot-to-wait-for-user-reply
# https://python-telegram-bot.readthedocs.io/en/latest/telegram.forcereply.html
def no_command_message(bot, update, user_data, groups):
    query = list(groups)
    state = ConversationHandler.END
    if user_data['no_command_caller'] == 'find':
        state = find(bot, update, args=query, user_data=user_data)
    elif user_data['no_command_caller'] == 'heybot':
        state = heybot(bot, update, query, user_data)
    elif user_data['no_command_caller'] == 'flibusta':
        state = flibusta(bot, update, query, user_data)
    del user_data['no_command_caller']
    return state


def heybot(bot, update, args=None, user_data=None):
    log.log_user(update)
    if args:
        reply = "Принято! Будет донесено начальству"
        log.log_bot(reply, update)
        update.message.reply_text(reply)
        return ConversationHandler.END
    else:
        reply = "Чем желаешь поделиться?"
        log.log_bot(reply, update)
        update.message.reply_text(reply)
        user_data['no_command_caller'] = 'heybot'
        return 404
