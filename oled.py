from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
import time
import datetime
import math
#import multiprocessing as mp
#from multiprocessing.sharedctypes import Value, Array
#import ctypes
import requests

API_URL = "http://localhost/api/v1/todos"

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

MAX_CHAR_ON_LINE = 21
LEFT_MARGIN = 4
TODO_TEXT_LINE_INDICES = [(LEFT_MARGIN, 0), (LEFT_MARGIN, 10), (LEFT_MARGIN, 20)]
TODO_DUEDATE_LINE_INDEX = (LEFT_MARGIN, 50)
POMODORO_TIMER_LINE_INDEX = (94, 50)

current_todo_id = -1

def oled_screen():
    # Box and text rendered in portrait mode
    while (True):
        time.sleep(0.5)

        current_todo = get_current_todo()

        with canvas(device) as draw:
            if(current_todo == None):
       	        draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text(TODO_TEXT_LINE_INDICES[0], "No todos yet", fill="white")
            else:
                todo_lines = get_todo_text_lines(current_todo)

       	        draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text(TODO_TEXT_LINE_INDICES[0], todo_lines[0], fill="white")
                draw.text(TODO_TEXT_LINE_INDICES[1], todo_lines[1], fill="white")
                draw.text(TODO_TEXT_LINE_INDICES[2], todo_lines[2], fill="white")
                if(current_todo['duedate'] != None):
                    draw.text(TODO_DUEDATE_LINE_INDEX, current_todo['duedate'], fill="white")
                draw.text(POMODORO_TIMER_LINE_INDEX, "25:00", fill="white")

def get_current_todo():
    global current_todo_id
    todos = requests.get(API_URL).json()
    todos = [todo for todo in todos if todo['isCompleted'] == 0]

    if(len(todos) == 0): return None
    if(current_todo_id == -1):
        #Initial todo
        current_todo_id = todos[0]['id']

    found_todo = None
    try:
        found_todo = [todo for todo in todos if todo['id'] == current_todo_id][0]
    except: pass
    if(found_todo == None and current_todo_id != -1):
        current_todo_id = -1
        return get_current_todo()

    return found_todo

def get_todo_text_lines(todo):
    result = [
        todo['text'][0 : MAX_CHAR_ON_LINE - 1],
        todo['text'][MAX_CHAR_ON_LINE : MAX_CHAR_ON_LINE * 2 - 1],
        todo['text'][MAX_CHAR_ON_LINE * 2 : MAX_CHAR_ON_LINE * 3 - 1]
    ]

    return result

