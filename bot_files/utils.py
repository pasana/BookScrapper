def prepare_next_books(user_data):
    if len(user_data['found_books']) > 5:
        user_data['found_books'] = user_data['found_books'][5:]
        reply_keyboard = [[str(x) for x in range(1, 6)], ["Отмена", "Дальше!"]]
    else:
        reply_keyboard = [[str(x) for x in range(1, len(user_data['found_books']) + 1)], ["Отмена"]]
        del user_data['found_books']
    return reply_keyboard
