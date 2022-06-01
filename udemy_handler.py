import udemy
import json
import Objects
import database

##############################
#  TRANSFORMATION FUNCTIONS #
############################


def course_list_to_links(courses):
    message = "\n"
    count = 0
    number_emojis = ['1️⃣', '2️⃣', '3️⃣']
    for course in courses:
        course_line = number_emojis[count]+' : \n'
        course_link = 'udemy.com/course/'+course.link
        message += course_line+course_link+'\n\n'

        count += 1

    return message


def courses_to_ids(courses):
    ids = []
    for course in courses:
        ids.append(str(course.unique))
    return ids


def course_list_to_message(courses):
    message = "\n\n"
    for course in courses:
        course_line = course.title+': \n'
        course_link = 'udemy.com/course/'+course.link
        message += course_line+course_link
        message += '\n\n'

    return message

##############################################
# UDEMY API COURSES FUNCTIONS               #
############################################


def recomend_courses_to_user(topic, user, lang='es', amount=1):
    """
    Selects courses of X topic from the database
    It excludes courses already recommended to the user
    If the quota of courses hasnt been fulfilled, then we search
    courses in the udemy API
    We add these courses to the database so that they can be
    recommended

    :param topic: The course topic
    :param user: Twitter user ID
    :param lang: language (for search purposes)
    :param amount: amount of courses to be recommended
    :return: List of courses
    """

    # Obtain courses from database which are not in user courses list
    courses = database.give_courses_to_user(topic, lang, user, amount)

    # If the courses from database satisfy the quota, it is not
    # necessary to use the Udemy API
    size = len(courses)
    if size >= amount:
        return courses

    # Determine the amount of courses with same keyword and language in database
    # Then, calculate the start page for udemy API
    # This serves to potentially reduce time of searching
    topic_count = database.count_keyword(topic, lang)
    start_page = max(1, topic_count//10)

    # Get new courses from Udemy API
    additional_courses = search_udemy_courses(topic, amount-size, size=10, page=start_page, lang=lang).values()

    # Store courses in database
    database.register_many_courses(additional_courses)

    #   Update id values of additional courses objects
    #   Obtain the unique keys from database

    updated_additional_courses = []

    for additional_course in additional_courses:
        additional_course_object = database.get_course_by_id(additional_course.id)
        updated_additional_courses.append(additional_course_object)

    # Add new courses objects to courses to return
    courses.extend(updated_additional_courses)

    return courses


def get_course_details(course_id):
    details = Client.get_coursesdetail(course_id)
    parsed_details = json.loads(details)
    return parsed_details


def get_course_for_top(topic, lang='es'):

    course = database.get_course_from_database(topic, lang)
    if course is None:
        course = search_udemy_course(topic, lang, order='newest')
        if course is not None:
            database.register_course(course, topic)

    return course


def search_udemy_course(topic, lang='es', size=10, page=1, tries=0, order='relevance'):

    # Udemy API request
    course_list = Client.get_courseslist(language=lang, search=topic, page_size=size, page=page, price="price-free",
                                         ordering=order)
    parsed_courses = json.loads(course_list)
    course_list = parsed_courses['results']
    amount = len(course_list)

    # If there are no courses we return an empty list
    if amount == 0 or tries >= 10:
        return None

    for course in course_list:
        course_id = int(course['id'])
        course_object = database.get_course_by_id(course_id)

        # If course is not none, then it is already in database
        if course_object is not None:
            continue

        course_title = course['title']
        course_link = course['url']
        course_link = course_link.replace('/course/', '')

        return Objects.Course(course_id, course_title, course_link, topic, lang=lang)


def search_udemy_courses(topic, amount, lang='es', size=10, page=1, tries=0, course_set=None, order='relevance'):

    if course_set is None:
        course_set = {}

    # If tried 2 times, change search settings to give priority to newer courses
    if tries == 2:
        page = 1
        order = 'newest'

    course_list = Client.get_courseslist(language=lang, search=topic, page_size=size, page=page, price="price-free",
                                         ordering=order)
    parsed_courses = json.loads(course_list)
    course_list = parsed_courses['results']
    course_amount = len(course_list)

    # If there are no courses we return an empty list
    if course_amount == 0 or (page*size) >= 10000 or tries >= 5:
        return course_set

    for course in course_list:

        course_id = int(course['id'])
        course_object = database.get_course_by_id(course_id)

        # If course is not none, then it is already in database
        if course_object is not None:
            continue

        course_title = course['title']
        course_link = course['url']
        course_link = course_link.replace('/course/', '')

        course_object = Objects.Course(course_id, course_title, course_link, topic, lang=lang)
        course_set.update({course_object.id: course_object})

        if len(course_set) >= amount:
            return course_set

    if len(course_set) >= amount:
        return course_set

    return search_udemy_courses(topic, amount, lang, size, page+1, tries+1, course_set, order=order)


# API INITIALIZATION
Client = udemy.PyUdemy(clientID="Your udemy client id",
                       clientSecret="your udemy api secret")


