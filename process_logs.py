import pprint
import re
from collections import Counter

ME = 3433299281

pattern = re.compile(r"(?P<m_type>(MESSAGE|BOT REPLY)) (from|to) .*: (?P<text>[\S ]*)", flags=re.UNICODE)

user_pattern_v1 = re.compile(r"(MESSAGE|BOT REPLY) (from|to) "
                             r"(?P<user_id>([0-9]*|[0-9]* \([\S]*\))): [\S ]*", flags=re.UNICODE)

user_pattern_v2 = re.compile(r"(MESSAGE|BOT REPLY) (from|to) "
                             r"(?P<user_id>([0-9]*|[0-9]* \([\S]*\))) "
                             r"\((?P<username>[\w]*)\): [\S ]*", flags=re.UNICODE)

user_pattern = re.compile(r"(MESSAGE|BOT REPLY) (from|to) "
                          r"(?P<user_id>([0-9]*|[0-9]* \([\S]*\))) "
                          r"\((?P<first_name>[\w]*) (?P<last_name>[\w]*) | (?P<username>[\w]*)\): [\S ]*",
                          flags=re.UNICODE)

command = re.compile(r"/[\w]+")


def get_user(line):
    try:
        return user_pattern.search(line).groupdict()
    except AttributeError:
        try:
            return user_pattern_v2.search(line).groupdict()
        except AttributeError:
            return user_pattern_v1.search(line).groupdict()


json_array = []
clean_data = set()
users = dict()
commands = list()
with open('bookscrapper_bot.log', 'r') as logs:
    data = logs.readlines()
    for line in data:
        res = pattern.search(line)
        if res:
            message = res.groupdict()
            print("%s: %s" % (line[:19], res.group(0)))
            clean_data.add("%s: %s" % (line[:19], res.group(0)))
            user = get_user(line)

            if message['m_type'] == 'MESSAGE' and user['user_id'] != ME:
                try:
                    commands += [command.search(message['text']).group(0)]
                except AttributeError:
                    pass

            if user['user_id'] in users:
                # check new fields
                if len(user) > len(users[user['user_id']]):
                    for key in user.keys():
                        if key != 'user_id' and key not in users[user['user_id']].keys():
                            users[user['user_id']][key] = user[key]
                users[user['user_id']]['messages_count'] += 1
            else:
                # add new user
                users[user['user_id']] = user
                users[user['user_id']]['messages_count'] = 1
                del users[user['user_id']]['user_id']

            item = {'time': line[:32]}
            item.update(user)
            item.update(message)
            json_array += [item]

print("USERS: ")
pprint.pprint(users)

pprint.pprint(Counter(commands))

print(len(json_array))
import json

json.dump(json_array, open('parsed_logs.json', 'w'))
