from transliterate import translit


def prepare_next_items(user_data, item_type):
    if len(user_data[item_type]) > 5:
        user_data[item_type] = user_data[item_type][5:]
        reply_keyboard = [[str(x) for x in range(1, 6)], ["Отмена", "Дальше!"]]
    else:
        reply_keyboard = [[str(x) for x in range(1, len(user_data[item_type]) + 1)], ["Отмена"]]
        del user_data[item_type]
    return reply_keyboard


def valid_filename(filename):
    # cyrillic characters doesn't work for some reason
    new_filename = translit('.'.join(filename.split('.')[:-1]), "ru", reversed=True)
    return new_filename + '.fb2'
