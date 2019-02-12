import logging


class Logger:
    ME = 3433299281

    def __init__(self):
        # create logger
        self.logger = logging.getLogger('USER_HISTORY')
        self.logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(ch)
        self.logger.info("Logger initiated")

    def check_user(self, update):
        if update.message.from_user.id != self.ME:
            return True
        return False

    def log_user(self, update):
        # if self.check_user(update):
        self.logger.info("MESSAGE from %d (%s %s | %s): %s" % (update.message.from_user.id,
                                                               update.message.from_user.first_name,
                                                               update.message.from_user.last_name,
                                                               update.message.from_user.username,
                                                               update.message.text.replace('\n', ' ')))

    def log_bot(self, text, update):
        self.logger.info("BOT REPLY to %d (%s %s | %s): %s" % (update.message.from_user.id,
                                                               update.message.from_user.first_name,
                                                               update.message.from_user.last_name,
                                                               update.message.from_user.username,
                                                               text.replace('\n', ' ')))
