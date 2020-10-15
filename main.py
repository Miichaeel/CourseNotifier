from CourseNotifier import CourseNotifier
from Twilio import Twilio
from WebSocCourses import Courses 
from SECRETS import *

def main():
    courses = Courses(CHROME_PATH)

    twilio = Twilio(TWILIO_SID, TWILIO_AUTHTOKEN, TWILIO_FROMNUMBER)

    notify = CourseNotifier(courses, twilio, TWILIO_TONUMBER, 60)

    notify.setCourseCodes("34000")

    notify.startWatch()

if __name__ == "__main__":
    main()
