import sqlite3
import time
import Objects
import settings_manager

# Database tables
db_file_name = "database"

user_table = "users"
course_table = "courses"
keyword_table = "keywords"
discounts_table = "discounts"

# User table field constants
user_id_field = "ID"
user_courses_field = "COURSES"
user_last = "LASTCONNECTED"
lang_field = "LANG"

# Course table field constants
course_id_field = "ID"
course_title_field = "TITLE"
course_url_field = "URL"
keyword_field = "keyword"
course_presented_field = "PRESENTED"
course_added_field = "ADDED"

# Keyword table field constants
keyword_field_table = "KEY"
keyword_count = "COUNT"

# Discount table field constants
coupon_field = "COUPON"


##############################################
# GENERAL DATABASE FUNCTIONS                #
############################################


def init():

    cursor = connection.cursor()

    create_statement = 'CREATE TABLE IF NOT EXISTS '

    # CREATE USER TABLE
    cursor.execute(create_statement+user_table+'('+user_id_field+' INTEGER, '+user_courses_field+' TEXT, '
                   + user_last+' INTEGER, '+lang_field+' TEXT)')

    # CREATE COURSE TABLE
    cursor.execute(create_statement+course_table+'('+course_id_field+' INTEGER, '+course_title_field
                   + ' TEXT, '+course_url_field+' TEXT, '+keyword_field+' TEXT, '+course_presented_field +
                   ' TEXT, '+course_added_field+' INTEGER, '+lang_field +
                   ' TEXT, UNIQUE_ID INTEGER PRIMARY KEY AUTOINCREMENT)')

    # CREATE KEYWORDS TABLE
    cursor.execute(create_statement+keyword_table+'('+keyword_field+' TEXT, '+keyword_count+' INTEGER, '+
                   lang_field+' TEXT)')

    # CREATE DISCOUNT TABLE
    cursor.execute(create_statement+discounts_table+'('+course_title_field+' TEXT, '+course_url_field+' TEXT, '
                   + course_presented_field+' INTEGER, ' + coupon_field+' TEXT, '+course_added_field+' INTEGER )')


##############################################
# USER DATABASE FUNCTIONS                   #
############################################


def register_user(twitter_id, lang):

    cursor = connection.cursor()
    timestamp = int(time.time())
    courses = ''
    cursor.execute('INSERT INTO '+user_table+' VALUES(?,?,?,?)', (twitter_id, courses, timestamp, lang))

    connection.commit()


def unregister_user(twitter_id):

    cursor = connection.cursor()
    cursor.execute('DELETE FROM '+user_table+' WHERE '+user_id_field+'=?', (twitter_id, ))

    connection.commit()


def update_user_data(user):

    cursor = connection.cursor()
    courses = Objects.list_to_string(user.courses)
    timestamp = int(time.time())
    cursor.execute('UPDATE '+user_table+' SET '+user_courses_field+'=?, '+user_last+'=? WHERE '+user_id_field+'=?',
                   (courses, timestamp, user.id))

    connection.commit()


def get_user_by_id(user_id):

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM '+user_table+' WHERE '+user_id_field+'=?', (user_id, ))
    user = Objects.query_to_user(cursor.fetchone())

    return user


##############################################
# COURSE DATABASE FUNCTIONS                 #
############################################


def register_course(course, keyword):

    cursor = connection.cursor()
    timestamp = int(time.time()/3600)
    presented = 0
    if course.presented is True:
        presented = 1

    args = (course.id, course.title, course.link, keyword, presented, timestamp, course.lang)
    fields = '('+course_id_field+','+course_title_field+','+course_url_field+','+keyword_field+',' +\
             course_presented_field+','+course_added_field+','+lang_field+')'
    cursor.execute('INSERT INTO '+course_table+fields+' VALUES(?,?,?,?,?,?,?)', args)

    connection.commit()


def register_many_courses(course_list):

    """
    Register many courses into the database.

    :param course_list: List of course objects
    """

    cursor = connection.cursor()
    fields = '(' + course_id_field + ',' + course_title_field + ',' + course_url_field + ',' + keyword_field + ',' + \
             course_presented_field + ',' + course_added_field + ',' + lang_field + ')'
    for course in course_list:
        presented = 0
        if course.presented is True:
            presented = 1

        args = (course.id, course.title, course.link, course.keywords, presented, course.added, course.lang)
        cursor.execute('INSERT INTO ' + course_table + fields + ' VALUES(?,?,?,?,?,?,?)', args)

    connection.commit()


def update_course(course):

    cursor = connection.cursor()
    presented = 0
    if course.presented is True:
        presented = 1

    args = (presented, course.id)
    cursor.execute('UPDATE '+course_table+' SET '+course_presented_field+'=? WHERE '
                   + course_id_field+'=?', args)

    connection.commit()


def get_course_by_id(course_id):

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM '+course_table+' WHERE '+course_id_field+'=?', [course_id])
    fetch = cursor.fetchone()
    course = Objects.query_to_course(fetch)

    return course


def give_courses_to_user(topic, lang, user=None, amount=1):

    cursor = connection.cursor()
    courses_taken = ''

    if user is not None:
        courses_taken = Objects.list_to_string(user.courses)

    args = (lang, topic)
    query = 'SELECT * from '+course_table+' WHERE UNIQUE_ID NOT IN ({}) AND '+lang_field+'=? AND ' + \
            keyword_field+'=?'
    query = query.format(courses_taken)
    print(query)
    cursor.execute(query, args)

    courses = []

    results = cursor.fetchall()

    count = 0
    if results is not None:
        for result in results:

            if count >= amount:
                break

            course = Objects.query_to_course(result)
            if course is not None:
                courses.append(course)
                count += 1

    print('Courses found: '+str(courses))

    return courses


def get_course_from_database(topic, lang):

    cursor = connection.cursor()

    cursor.execute('SELECT * FROM '+course_table+' WHERE '+keyword_field+'=? AND '+lang_field+'=? AND ' +
                   course_presented_field + '= 0 ORDER BY RANDOM() LIMIT 1', (topic, lang))

    result = cursor.fetchone()

    return Objects.query_to_course(result)


def get_amount_of_courses(keyword, lang='es'):
    cursor = connection.cursor()
    cursor.execute('SELECT COUNT('+course_id_field+') FROM '+course_table+' WHERE '+keyword_field+'=? AND '+lang_field +
                   '=?', (keyword, lang))
    result = cursor.fetchone()

    return int(result[0])


def clean_old_courses():

    cursor = connection.cursor()
    sub_hours = int(settings_manager.settings.get('delete_delay'))
    hours_since_epoch = int(time.time() / 3600)
    before_hours = hours_since_epoch - sub_hours
    cursor.execute('DELETE FROM ' + course_table + ' WHERE ' + course_added_field + ' <= ?', (before_hours,))

    connection.commit()

##############################################
# KEYWORD DATABASE FUNCTIONS                #
############################################


def count_keyword(keyword, lang=None):

    cursor = connection.cursor()
    if lang is not None:
        cursor.execute('SELECT '+keyword_count+' FROM '+keyword_table+' WHERE '+keyword_field+'=? AND '+lang_field+'=?'
                       , (keyword, lang))
    else:
        cursor.execute('SELECT '+keyword_count+' FROM '+keyword_table+' WHERE '+keyword_field+'=?', (keyword, ))
    results = cursor.fetchone()

    if results is None:
        return 0

    return int(results[0])


def register_keyword(keyword, lang='es'):

    amount = count_keyword(keyword)

    cursor = connection.cursor()
    if amount == 0:
        cursor.execute('INSERT INTO '+keyword_table+' VALUES(?, ?, ?)', (keyword, amount+1, lang))
    else:
        cursor.execute('UPDATE '+keyword_table+' SET '+keyword_count+'=? WHERE '+keyword_field+'=? AND '
                       + lang_field+'=?',
                       (amount+1, keyword, lang))

    connection.commit()


def get_top_keywords(amount=1, lang=None):
    """
    Gets the top X keywords with highest demand (according to user interaction)
    If no keywords is found, an empty list is returned so that it can be handled
    in the twitter module

    :param amount: Amount of numbers to be included (e.g. amount=10 1-10)
    :param lang: Language of the keywords (If none, it will be ignored in query)
    :return: List with keywords
    """

    cursor = connection.cursor()

    if lang is None:
        cursor.execute('SELECT '+keyword_table+'.'+keyword_field+' FROM '+keyword_table+' ORDER BY ' +
                       keyword_table+'.'+keyword_count+' DESC')
    else:
        cursor.execute('SELECT ' + keyword_table + '.' + keyword_field + ' FROM ' + keyword_table +
                       ' WHERE '+lang_field+'=?'+' ORDER BY ' + keyword_table + '.' + keyword_count + ' DESC', (lang,))
    results = cursor.fetchall()

    keywords = []

    if results is not None:
        for record in results:
            keywords.append(record[0])

    if len(keywords) >= amount:
        keywords = keywords[:amount]

    return keywords

##############################################
# DISCOUNT DATABASE FUNCTIONS               #
############################################


def register_discount(discount_course):
    cursor = connection.cursor()
    timestamp = int(time.time() / 3600)

    presented = 0
    if discount_course.presented is True:
        presented = 1

    args = (discount_course.title, discount_course.url, presented, discount_course.coupon, timestamp)
    cursor.execute('INSERT INTO '+discounts_table+' VALUES(?,?,?,?,?)', args)

    connection.commit()


def register_discounts(discount_courses):

    cursor = connection.cursor()
    timestamp = int(time.time() / 3600)

    for discount_course in discount_courses:

        presented = 0
        if discount_course.presented is True:
            presented = 1

        args = (discount_course.title, discount_course.url, presented, discount_course.coupon, timestamp)
        cursor.execute('INSERT INTO ' + discounts_table + ' VALUES(?,?,?,?,?)', args)

    connection.commit()


def unregister_discount(discount_title):

    cursor = connection.cursor()
    cursor.execute('DELETE FROM '+discounts_table+' WHERE '+course_title_field+'=? ', (discount_title, ))
    connection.commit()


def get_discount_by_title(discount_title):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM '+discounts_table+' WHERE '+course_title_field+'=?', (discount_title, ))
    result = cursor.fetchone()

    return Objects.query_to_discount(result)


def remove_by_date():

    cursor = connection.cursor()
    sub_hours = int(settings_manager.settings.get('delete_delay'))
    hours_since_epoch = int(time.time()/3600)
    before_hours = hours_since_epoch-sub_hours
    cursor.execute('DELETE FROM '+discounts_table+' WHERE '+course_added_field+' <= ?', (before_hours, ))

    connection.commit()


def update_discount(discount_course):

    cursor = connection.cursor()
    presented = 0
    if discount_course.presented is True:
        presented = 1

    args = (presented, discount_course.title)
    cursor.execute('UPDATE '+discounts_table+' SET '+course_presented_field+'=? WHERE '+course_title_field+'=?', args)
    connection.commit()


def update_discounts(discount_list):

    cursor = connection.cursor()
    for discount in discount_list:
        presented = 0
        if discount.presented is True:
            presented = 1

        args = (presented, discount.title)
        cursor.execute(
            'UPDATE ' + discounts_table + ' SET ' + course_presented_field + '=? WHERE ' + course_title_field + '=?',
            args)

    connection.commit()


def get_unposted_discounts():

    courses = []

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM '+discounts_table+' WHERE '+course_presented_field+'=0')
    results = cursor.fetchall()

    if results is not None:
        for result in results:

            discount_course = Objects.query_to_discount(result)
            if discount_course is not None:
                courses.append(discount_course)

    return courses


# INITIALIZATION
connection = sqlite3.connect(db_file_name, check_same_thread=False)

init()
