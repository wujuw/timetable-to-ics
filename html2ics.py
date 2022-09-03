from array import array
from calendar import calendar
from datetime import datetime, timedelta
from operator import le
import uuid
from bs4 import BeautifulSoup
import re
from icalendar import Calendar, Event

from pytz import timezone

calendar = Calendar(calendar_name = "课程表")

time_dict = {
    1: [(8, 30), (9, 15)],
    2: [(9, 20), (10, 5)],
    3: [(10, 20), (11, 5)],
    4: [(11, 10), (11, 55)],
    5: [(14, 30), (15, 15)],
    6: [(15, 20), (16, 5)],
    7: [(16, 20), (17, 5)],
    8: [(17, 10), (17, 55)],
    9: [(19, 30), (20, 15)],
    10: [(20, 20), (21, 5)],
    11: [(21, 10), (21, 55)],
    12: [(22, 00), (22, 45)],
}
begin_year = 2022
begin_month = 8
begin_day = 29 # 周一

cls_lst = [
        {
            'name': '课程A',
            'teacher': '教师名称',
            'room': '教室',
            'time': [time_dict[1], time_dict[2]], # 第一节课-第二节课
            # 1 ... 15 周
            'week': [1, 15],
            'day': [1, 3] # 周一、周三
        },
]

def create_event(lesson_name, classroom, teacher, start, end):
    # 创建事件/日程
    event = Event()
    event.add('summary', lesson_name)
    tz_utc_8 = timezone('Asia/Shanghai')
    dt_now = datetime.now(tz=tz_utc_8)
    event.add('dtstart', start)
    event.add('dtend', end)
    # 创建时间
    event.add('dtstamp', dt_now)
    event.add('LOCATION', classroom)
    event.add('DESCRIPTION', '教师：' + teacher)
    # UID保证唯一
    event['uid'] = str(uuid.uuid1()) + '/whhxd@outlook.com'

    return event


def get_lesson(course_info, day):
    # case 1100016004/矩阵理论(8班)/60/3/王转德/1-15周/(5~6)/品学楼B208
    course_name = course_info[1].replace('\\', '')   
    course_teacher = course_info[4]
    course_week = course_info[5].replace('周', '').split('-')
    course_time = course_info[6].replace('(', '').replace(')', '').split('~')
    course_location = course_info[7]
    start = datetime(begin_year, begin_month,
                              begin_day, time_dict[int(course_time[0])][0][0], time_dict[int(course_time[0])][0][1]) + timedelta(days=day)
    end = datetime(begin_year, begin_month, begin_day, time_dict[int(course_time[1])][1][0], time_dict[int(course_time[1])][1][1]) + timedelta(days=day)
    return {'name': course_name, 'teacher': course_teacher, 'room': course_location, 'time': [start, end], 'week': [int(course_week[0]), int(course_week[1])], 'day': day}



soup = BeautifulSoup(open('newtable.html'), 'html.parser')

timetable = [[[] for x in range(7)] for y in range(5)]

table = soup.find('table', id='tbl')
# delete the first row
table.tr.decompose()
# delete the first column
for row in table.find_all('tr'):
    row.td.decompose()

# iterate over rows
for i, row in enumerate(table.find_all('tr')):
    # iterate over cells
    for j, cell in enumerate(row.find_all('td')):
        # get the text
        text = cell.get_text()
        if text:
            curriculum = text.split('，\n')
            for course in curriculum:
                course = re.sub('[\n\t\r]', '', course)
                # case 1100016004/矩阵理论(8班)/60/3/王转德/1-15周/(5~6)/品学楼B208
                course_info = course.split('/')
                # if len
                if len(course_info) == 8:
                    lesson = get_lesson(course_info, j)
                    for week in range(lesson['week'][0], lesson['week'][1] + 1):
                        start = lesson['time'][0] + timedelta(weeks=week - 1)
                        end = lesson['time'][1] + timedelta(weeks=week - 1)
                        calendar.add_component(create_event(lesson['name'], lesson['room'], lesson['teacher'], start, end))

with open('timetable.ics', 'wb') as f:
    f.write(calendar.to_ical())
