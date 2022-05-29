import time

import tweepy

import Objects
import settings_manager
import database
import udemy_handler
from langdetect import detect
import language_handler
from scraping import coupon_scraper
import random


# OAuth2
bearer = 'your twitter bearer token'
consumer_key = 'your api key'
consumer_key_secret = 'your api secret'
access_key = 'your access key'
access_key_secret = 'your access secret'

client = tweepy.Client(bearer, consumer_key, consumer_key_secret, access_key, access_key_secret)

auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_key, access_key_secret)
api = tweepy.API(auth)

# Create client session for bot
bot_user = client.get_user(username="GratisBot")
identifier = 1522997708809814018


def reply_to_user(status, messages, courses=[]):
    """
    Using tweepy, the method replies to a specific tweet with the courses as text

    :param status: The tweet to reply to
    :param messages: Result messages (e.g. syntax errors, success) List
    :param courses: List of courses to be posted
    :return: None
    """

    # Get courses as string format (title, url)
    courses_msgs = udemy_handler.course_list_to_message(courses)
    print(courses)
    messages.reverse()

    # Required by Tweepy to reply an user
    username = '@'+api.get_user(user_id=status.user.id_str).screen_name

    hashtags = '\n #udemyfree #udemygratis #udemy'

    messages.insert(0, username)
    tweet = '\n'.join(messages)

    # Handle variation of tweet format according to number of courses
    if len(courses) >= 2:
        if len(tweet)+len(courses_msgs)+len(hashtags) >= 280:
            courses_msgs = udemy_handler.course_list_to_links(courses)

    tweet += courses_msgs+hashtags

    # Reply to user, if not duplicated
    try:
        api.update_status(tweet, in_reply_to_status_id=status.id)
    except tweepy.TweepyException:
        print('Error while tweeting, maybe its duplicated, ignoring...')

    # Update id of last tweet (for the next check)
    settings_manager.settings.update({'last_twitt_id_check': str(status.id)})


def check_users_replies():
    """
    Using tweepy, searches through all the mentions done after a specific tweet id.
    It parses the user's tweet and replies with the courses about the requested topic.
    Every tweet searched, the latest tweet id is updated.

    :return: None
    """
    last_id = int(settings_manager.settings.get('last_twitt_id_check'))
    mentions = client.get_users_mentions(identifier, since_id=last_id)

    # If there are no responses since Id, we ignore the mentions
    if mentions[0] is None:
        print('No new mentions since '+str(last_id)+' ignoring...')
        return

    # Read mentions from json
    mentions = mentions[0]

    for mention in mentions:
        status = api.get_status(mention.id)

        user_id = int(status.user.id_str)

        # Ignore if reply comes from bot
        if user_id == identifier:
            continue

        # Evaluates if user follows bot
        friendship = api.get_friendship(source_id=identifier, target_id=status.user.id_str)[0]
        follows = bool(friendship.followed_by)

        # Checks if user already exists in database
        user = database.get_user_by_id(status.user.id_str)
        print('user: '+str(user))
        messages = []
        courses = []
        quantity, topic, lang = request_parser(message=mention.text)

        if (user is not None) and (follows is False):
            database.unregister_user(user.id)
            messages.append(language_handler.get_message('follow_me', lang))
        elif user is None:

            if follows is True:

                database.register_user(status.user.id_str, lang)
                messages.append(language_handler.get_message('followed', lang))
            else:
                messages.append(language_handler.get_message('follow_me', lang))

            user = Objects.User(status.user.id_str, [])

        if topic is not None:
            courses = udemy_handler.recomend_courses_to_user(topic, user, lang, quantity)

            if len(courses) >= 1:

                ids = udemy_handler.courses_to_ids(courses)
                user.courses.extend(ids)
                print(user.courses)

                database.update_user_data(user)
                database.register_keyword(topic, lang)
                messages.append(language_handler.get_message('courses_found', lang))
            else:
                messages.append(language_handler.get_message('no_courses_found', lang))
        else:
            messages.append(language_handler.get_message('syntax_error', lang))

        reply_to_user(status, messages, courses)

    settings_manager.save_settings()


def identify_language(message):
    """
    Uses langdetect function to identify the tweet's language.
    In case there is a misconception, there are additional checks (splly for spanish and portuguese)
    :param message: The message to evaluate
    :return: lang (String): Represents lang in iso 639-1 code
    """
    lang = detect(message)

    if lang != "es" and ("dame" in message) and ("curso" in message) and ("um" not in message):
        return "es"

    if lang != 'en' and ('give' in message) and ('course' in message or 'courses' in message):
        return 'en'

    return lang


def request_parser(message):
    """
    Gets a message as input and parses it.
    First it identifies the language of the message
    Then it tries to retrieve basic information such as amount and topic.
    :param message: The message to parses
    :return: tuple (quantity, topic, language)
    """

    command = message.replace('@GratisBot', '')
    command = command.replace('(', '').replace(')', '')
    command = command.strip()
    command = command.lower()
    to_evaluate = command[: command.rindex(' ')]
    language = identify_language(to_evaluate)
    quantity = 0
    topic = None
    print(language)
    if language == "es":
        quantity, topic = language_handler.handle_spanish(command)
    elif language == 'en':
        quantity, topic = language_handler.handle_english(command)

    elif language == 'de':
        quantity, topic = language_handler.handle_german(command)

    elif language == 'fr':
        quantity, topic = language_handler.handle_french(command)

    elif language == 'pt':
        quantity, topic = language_handler.handle_portuguese(command)
    print(quantity, topic)
    if topic == "":
        topic = None

    return quantity, topic, language


def post_discounts():
    """
    Gets discounts that are not yet published. If amount doesnt meet quota,
    it scrapes courses from udemyfreebies.com
    :return: None
    """
    init_time = time.time()
    print('Posting discounts...')

    # Remove potential older discounts
    database.remove_by_date()

    amount = int(settings_manager.settings.get('max_discounts_per_tweet'))
    discounts = database.get_unposted_discounts()
    discount_amount = len(discounts)

    # If discounts in DB dont meet quota, scrapes for discounts
    if discount_amount < amount:

        # Update all discounts found on database
        for discount in discounts:
            discount.presented = True
        database.update_discounts(discounts)

        diff = amount - discount_amount
        new_discounts = coupon_scraper.get_current_discounts()
        discounts.extend(new_discounts)
        if len(discounts) >= amount:
            discounts = discounts[:amount]

            # Updates presented status for all new discounts
            for discount in new_discounts[0:diff]:
                discount.presented = True

        # Register new discounts found
        database.register_discounts(new_discounts)

    else:

        # Update only the required amount of discounts in database
        for discount in discounts[0:amount]:
            discount.presented = True
        database.update_discounts(discounts)

    tweet_discounts(discounts, 0)
    print('Discounts posted. Took '+str(time.time()-init_time)+' s')


def tweet_discounts(discount_list, tries=0):
    """Gets a list of discounts and orginizes them in a way that they can be twitted.
       Since Twitter limits duplicate tweets, the bot shuffles the list to get a random value.
       In case it still is duplicated, retries again with a different order
    """
    if len(discount_list) == 0 or tries >= 5:
        return

    intro_text_es = language_handler.get_message('discount_intro', 'es')
    intro_text_en = language_handler.get_message('discount_intro', 'en')

    discounts = discount_list
    random.shuffle(discount_list)

    hashtags = '\n #udemyfree #udemygratis #udemy'
    intro_text = intro_text_es+'\n'+intro_text_en+'\n'

    try:

        first_discount = discounts[0]
        url = 'udemy.com/course/' + first_discount.url + '/?couponCode=' + first_discount.coupon
        intro_text += '\n\n\n'+first_discount.title+': \n'+ url + '\n\n' + '🧵...'
        intro_text += hashtags

        response = client.create_tweet(text=intro_text)
        status_id = response.data.get('id')

        for discount in discounts[1:]:

            url = 'udemy.com/course/'+discount.url+'/?couponCode='+discount.coupon
            text = discount.title + ': \n' + url
            status_id = api.update_status(text, in_reply_to_status_id=status_id).id

    except tweepy.TweepyException:
        tweet_discounts(discount_list, tries+1)


def post_hot_topics(lang='es'):
    """
    Gets the courses from the most requested topics stored in the database
    :param lang: Language of the courses to search (in iso 639-1)
    :return: None
    """

    amount = 5
    keywords = database.get_top_keywords(amount, lang)

    # If quota of top keywords is not met, add the default ones
    if len(keywords) < amount:
        keywords.extend(settings_manager.settings.get('default_topics').split(',')[:(amount-len(keywords))])

    print(keywords)
    courses = []

    for keyword in keywords:

        course = udemy_handler.get_course_for_top(keyword, lang)
        courses.append(course)

    # If no result with current top topics (e.g. trolling by rare keywords, search predefined keywords)

    if len(courses) == 0:
        keywords = settings_manager.settings.get('default_topics').split(',')[:amount]

        for keyword in keywords:
            course = udemy_handler.get_course_for_top(keyword, lang)
            courses.append(course)

    if len(courses) == 0:
        return

    # Tweet message formatting
    hashtags = '\n #udemyfree #udemygratis #udemy'

    intro_text = language_handler.get_message('top_courses_intro', lang)
    first_course = courses[0]
    intro_text += '\n\n\n'+first_course.title+': \n'+'udemy.com/course/'+first_course.link+ '\n\n' + '🧵...'
    intro_text += hashtags

    first_course.presented = True
    database.update_course(first_course)

    response = client.create_tweet(text=intro_text)
    status_id = response.data.get('id')
    index = 1

    # For every course, tweet its link and tittle with hashtags associated with its keyword
    # Finally, update the course in DB to show it has already been posted
    for course in courses[1:]:
        text = course.title+': \n'+'udemy.com/course/'+course.link
        text += '\n\n'+hashtags+' #'+keywords[index].replace(' ', '')
        status_id = api.update_status(text, in_reply_to_status_id=status_id).id
        course.presented = True
        database.update_course(course)
        index += 1


def try_parser(text):
    """
    Tests how the bot parses different text
    :param text: The text to test
    :return: quantity (int), (str) topic, (str) language
    """
    quantity, topic, language = request_parser(text)
    return quantity, topic, language


def sim_tweet():
    """
    Simulates as if a twitter user is requesting a course through a tweet.
    Doesnt tweet anything, but it can add courses to the database and edit
    the users courses. It is intended to be called inside a get request

    :return: list of courses
    """
    init_time = time.time()*1000

    text = "@GratisBot Gibt mir zwei Kurse uber Java"
    quantity, topic, language = try_parser(text)
    user = database.get_user_by_id(1590242809)
    if user is None:
        user = Objects.User(1590242809, [])
        database.register_user(user.id, 'es')

    if topic is None:
        error = (language_handler.get_message('syntax_error', language))
        return error

    courses = udemy_handler.recomend_courses_to_user(topic, user, language, int(quantity))

    ids = udemy_handler.courses_to_ids(courses)
    user.courses.extend(ids)
    database.update_user_data(user)

    if len(courses) == 0:
        error = (language_handler.get_message('no_courses_found', language))
        return error

    database.register_keyword(topic, language)
    time_elapsed =(time.time()*1000)-init_time
    print('Time elapsed: '+str(time_elapsed)+' ms')

    return udemy_handler.course_list_to_message(courses)


def sim_top(lang='es'):
    """
    Tests how the bot stores/tweets courses from top X most requested keywords.
    Intended to be called inside get function.

    :param lang: Language of courses
    :return: None
    """
    amount = 5
    keywords = database.get_top_keywords(amount, lang)
    if len(keywords) < amount:
        keywords.extend(settings_manager.settings.get('default_topics').split(',')[:(amount - len(keywords))])

    print(keywords)
    courses = []

    for keyword in keywords:
        course = udemy_handler.get_course_for_top(keyword, lang)
        courses.append(course)

    # If no result with current top topics (e.g. trolling by rare keywords, search predefined keywords)

    if len(courses) == 0:
        keywords = settings_manager.settings.get('default_topics').split(',')[:amount]

        for keyword in keywords:
            course = udemy_handler.get_course_for_top(keyword, lang)
            courses.append(course)

    for course in courses:
        print(course.title)
