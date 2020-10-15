from html.parser import HTMLParser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import NoSuchElementException

WEBSOC = 'https://www.reg.uci.edu/perl/WebSoc'

class WebSocParser(HTMLParser):

    def __init__(self, firstTitle: str, dataText: [str], HTMLdata: [str]):
        super(WebSocParser, self).__init__()
        self.HTMLdata = HTMLdata
        self.data = dict()
        self.hData = list()
        self._RENAMETHIS(firstTitle, dataText)
        self._parse()

    def handle_data(self, data) -> None:
        self.hData.append(data)

    def _RENAMETHIS(self, firstTitle: str, dataText: [str]) -> None:
        startIndex = dataText.index(firstTitle)

        onTitle = True

        currentTitle = " ".join(firstTitle.replace("(Prerequisites)", "").replace("(Co-courses)", "").split())
    
        for desc in dataText[startIndex:]:
            if desc != "":
                if onTitle:
                    currentTitle = " ".join(desc.replace("(Prerequisites)", "").replace("(Co-courses)", "").split())
                    self.data[currentTitle] = list()
                    onTitle = False
                    
                elif "(same as" not in desc and "Code Type Sec" not in desc:
                    self.data[currentTitle].append((desc.split()[0]))
            else:
                onTitle = True

    def _getCourseCodes(self, data: [[str]]) -> {str: str}:
        courseInfo = dict()

        for info in data:
            if len(info) > 0 and info[0].isdigit():
                length = len(info)
                courseInfo[info[0]] = {
                    "Code": info[length-length].replace("\xa0", ""),
                    "Type": info[length-length+1].replace("\xa0", ""),
                    "Sec": info[length-length+2].replace("\xa0", ""),
                    "Units": info[length-length+3].replace("\xa0", ""),
                    "Instructor": (" & ".join(info[length-length+4:length-11])),
                    "Time": info[length-11].replace("\xa0", ""),
                    "Place": info[length-10].replace("\xa0", ""),
                    "Final": info[length-9].replace("\xa0", ""),
                    "Max": info[length-8].replace("\xa0", ""),
                    "Enr": info[length-7].replace("\xa0", ""),
                    "WL": info[length-6].replace("\xa0", ""),
                    "Req": info[length-5].replace("\xa0", ""),
                    #"Nor": info[length-5].replace("\xa0", ""),
                    "Rstr": info[length-4].replace("\xa0", ""),
                    "Textbooks": info[length-3].replace("\xa0", ""),
                    "Web": info[length-2].replace("\xa0", ""),
                    "Status": info[length-1].replace("\xa0", "")
                 }

        return courseInfo

    def _stripHTML(self) -> [[str]]:
        data = list()
        
        for html in self.HTMLdata:
            self.feed(html)
            
            data.append(self.hData)
            
            self.hData = list()

        return data

    def _parse(self):
        data = self._stripHTML()

        courseInfo = self._getCourseCodes(data)

        for courseCodes in self.data.values():
            for code in range(len(courseCodes)):
                length = courseInfo[courseCodes[code]]

                courseCodes[code] = courseInfo[courseCodes[code]]

    def getData(self) -> [str]:
        return self.data

class Courses:

    def __init__(self, chromePATH: str):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        self.driver = webdriver.Chrome(chromePATH, options=options)
        self.courses = dict()

    def _enterCourseCodes(self, courseCodes: str) -> None:
        search = self.driver.find_element_by_name("CourseCodes")
        search.send_keys(courseCodes)

    def _fillForm(self, query: {str: str}) -> None:
        #TODO: Implement remaining query options.
        if 'CourseCodes' in query and query['CourseCodes']:
            self._enterCourseCodes(query['CourseCodes'])

    def _downloadData(self, query: {str: str}) -> object:
        self._fillForm(query)

        submit = self.driver.find_element_by_name("Submit")

        submit.click()

        try: 
            dataElements = self.driver.find_element_by_class_name("course-list").find_elements_by_tag_name("tr")
            
        except NoSuchElementException:
            #TODO: Implement actual error message from WebSoc.
            raise KeyError("Error: Invalid query.")
            
        else:
            if len(dataElements) > 0:
                firstTitle = self.driver.find_element_by_class_name("CourseTitle").text

                dataText = [data.text for data in dataElements]

                data = [html.get_attribute("innerHTML") for html in dataElements]

                parser = WebSocParser(firstTitle, dataText, data)
                
                return parser.getData()
            else:
                #TODO: Implement actual error message from WebSoc.
                raise ValueError("Error: No courses with given query exist.")
            

    def searchCourses(self, query: {str: str}) -> None:
        self.driver.get(WEBSOC)

        data = self._downloadData(query)

        self.courses = data


    def getCourses(self) -> {str: [str]}:
        return self.courses


