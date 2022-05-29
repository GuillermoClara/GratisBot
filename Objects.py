import time


class User:
    def __init__(self, user_id, courses, last_connected=int(time.time()/3600), lang='es'):

        self.id = user_id
        self.courses = courses
        self.last = last_connected
        self.lang = lang


class Course:
    def __init__(self, identifier, title, link, keywords, presented=False, added=int(time.time()/3600), lang="es",
                 unique=0):

        self.id = identifier
        self.title = title
        self.link = link
        self.keywords = keywords
        self.lang = lang
        self.unique = unique
        self.presented = presented
        self.added = added


class DiscountCourse:

    def __init__(self, title, url, presented, coupon, date=int(time.time()/3600)):
        self.title = title
        self.url = url
        self.presented = presented
        self.coupon = coupon
        self.date = date


def query_to_user(query):
    if query is None:
        return None

    identifier = int(query[0])
    courses = string_to_list(query[1])
    print(courses)
    last = int(query[2])
    lang = query[3]
    return User(identifier, courses, last, lang)


def query_to_course(query):

    if query is None:
        return None

    identifier = int(query[0])
    title = query[1]
    link = query[2]
    keywords = query[3]

    presented = False
    if int(query[4]) != 0:
        presented = True

    added = int((query[5]))
    lang = query[6]
    unique = int(query[7])
    return Course(identifier, title, link, keywords, presented, added, lang, unique)


def query_to_discount(query):
    if query is None:
        return None

    title = query[0]
    url = query[1]

    presented = False
    if int(query[2]) == 1:
        presented = True

    coupon = query[3]
    added = int(query[4])

    return DiscountCourse(title, url, presented, coupon, added)


def string_to_list(string):

    if string == '':
        return []

    return string.split(',')


def list_to_string(sequence):

    if len(sequence) > 0:
        return ','.join(sequence)
    else:
        return ''
