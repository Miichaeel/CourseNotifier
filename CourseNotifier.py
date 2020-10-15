from Twilio import Twilio
from WebSocCourses import Courses 

import time


class CourseNotifier():

    def __init__(self, courses: Courses, twilio: Twilio, notifee: str, refreshRate: int):
        self.courses = courses
        self.twilio = twilio
        self.notifee = notifee
        self.refreshRate = refreshRate
        self.query = {
            "CourseCodes": ""
        }

    def getQuery(self):
        return self.query

    def setCourseCodes(self, codes: str) -> None:
        self.query["CourseCodes"] = codes

    def _removeCourse(self, title: str, courseInfo={}):
        if courseInfo:
            self.watchList[title].remove(courseInfo)
   
        for title, courses in self.watchList.copy().items():
            for course in courses:
                if course["Status"] == "OPEN":
                    self.watchList[title].remove(course)

            if not self.watchList[title]:
                self.watchList.pop(title)

    def notify(self, title: str, course: {str, str}) -> None:
        self.twilio.sendSMS(self.notifee,   
                                (f"CourseNotifier: {title} {course['Type']} "
                                f"{course['Sec']} {course['Code']} changed to OPEN and " 
                                f"has {int(course['Max'])-int(course['Enr'])} available seats.")
                        )

    def startWatch(self):
        self.courses.searchCourses(self.query)

        self.watchList = self.courses.getCourses()

        while self.watchList:
            self._removeCourse("")

            self.courses.searchCourses(self.query)

            recheckWatchList = self.courses.getCourses()

            for title, courses in self.watchList.copy().items():
                for course in courses:
                    newCourseInfo = [newCourse for newCourse in recheckWatchList[title] if newCourse["Code"] == course["Code"]][0]
                    if newCourseInfo["Status"] == "OPEN":
                        self.notify(title, newCourseInfo)
                        self._removeCourse(title, course)
    
            time.sleep(self.refreshRate)
      

