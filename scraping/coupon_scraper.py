
from bs4 import BeautifulSoup
import requests

from datetime import date

import Objects
import database


def get_current_discounts():
    """
    Gets a list of 100% off courses from udemyfreebies.com.
    It stops until a course discovered has already been added to DB or when it was posted the day before

    :return: courses: List of discount courses
    """
    courses = []

    # Get today's date
    today_date = str(date.today().day)
    course_date = today_date
    page = 1

    # Scrape the website until a course with a different post date is discovered
    # Each iteration, the bot will scrape the next page of the website search
    while course_date == today_date:

        # BeautifulSoup to parse html
        url = 'https://www.udemyfreebies.com/free-udemy-courses/' + str(page)

        html_text = requests.get(url, header).text

        soup = BeautifulSoup(html_text, 'html.parser')

        # Get all coupon div elements in the page
        coupons = soup.findAll('div', class_='theme-block')

        # For each coupon extract data and analyze
        for coupon in coupons:

            added = coupon.find('small', class_='text-muted').text
            added = added.split(' ')

            course_date = added[0]

            if course_date != today_date:
                break

            name = coupon.find('h4').find('a').text

            discount_course = database.get_discount_by_title(name)
            if discount_course is not None:
                continue

            # If course is already expired, ignore it
            button_detail = coupon.find('a', class_='button-icon').find('span').text.strip()
            if button_detail == 'Expired':
                continue

            price = coupon.find('div', class_='coupon-details-extra-3').find('del')
            if price is None:
                continue

            detailed_url = coupon.find('a', class_='button-icon').get('href')
            detailed_url = detailed_url.replace('free-udemy-course', 'out')

            # Parse URL and COUPON
            response = requests.get(detailed_url, header)
            detailed_url = response.url
            detailed_url = detailed_url.replace('https://www.udemy.com/course/', '')
            course_url, course_coupon = detailed_url.split('/')
            course_coupon = course_coupon[course_coupon.find('=') + 1:]

            # From parsed data, create new discount course and add it to list
            discount = Objects.DiscountCourse(name, course_url, False, course_coupon)
            courses.append(discount)

        # Each outer iteration go to next page
        page += 1

        return courses


header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "99.0.4844.51 Safari/537.36",
        "X-Amzn-Trace-Id": "Root=1-6228d3e0-1613b48566e186fd4764b5f9"}


