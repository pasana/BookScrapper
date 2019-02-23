import os

bot_token = os.environ['TELEGRAM_TOKEN']

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler

from logger import Logger

log = Logger()

from bot_files.basic import *
from bot_files.random import random_book
from bot_files.flibusta import flibusta, flibusta_book
from bot_files.find import book, find_book, author, series, find, \
    display_books, display_authors, display_series


# logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


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
        entry_points=[CommandHandler('find', find, pass_args=True, pass_user_data=True)],
        states={

            12: [RegexHandler('\d', book, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', find_book, pass_user_data=True),
                 RegexHandler('Книги', display_books, pass_user_data=True),
                 RegexHandler('Авторы', display_authors, pass_user_data=True),
                 RegexHandler('Серии книг', display_series, pass_user_data=True),
                 ],
            13: [RegexHandler('\d', author, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', find_book, pass_user_data=True)
                 ],
            21: [RegexHandler('\d', book, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', display_books, pass_user_data=True)
                 ],
            22: [RegexHandler('\d', author, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', display_authors, pass_user_data=True)
                 ],
            23: [RegexHandler('\d', series, pass_user_data=True),
                 RegexHandler('Отмена', cancel, pass_user_data=True),
                 RegexHandler('Дальше!', display_series, pass_user_data=True)
                 ]

        },
        fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)],
        allow_reentry=True
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
