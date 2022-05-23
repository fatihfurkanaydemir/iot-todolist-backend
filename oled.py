from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from threading import Thread
import time
import requests
import pigpio

API_URL = "http://localhost/api/v1/todos"

MAX_CHAR_ON_LINE = 20
LEFT_MARGIN = 4
TODO_TEXT_LINE_INDICES = [(LEFT_MARGIN, 0), (LEFT_MARGIN, 10), (LEFT_MARGIN, 20), (LEFT_MARGIN, 30)]
TODO_DUEDATE_LINE_INDEX = (LEFT_MARGIN, 50)
POMODORO_TIMER_LINE_INDEX = (94, 50)

POMODORO_TIME = 10

GPIO_PREV_PIN = 26
GPIO_MARK_PIN = 25
GPIO_NEXT_PIN = 24
GPIO_TIMER_PIN = 23

pi = pigpio.pi()
pi.set_mode(GPIO_PREV_PIN, pigpio.INPUT)
pi.set_mode(GPIO_MARK_PIN, pigpio.INPUT)
pi.set_mode(GPIO_NEXT_PIN, pigpio.INPUT)
pi.set_mode(GPIO_TIMER_PIN, pigpio.INPUT)

pi.set_glitch_filter(GPIO_PREV_PIN, 10000)
pi.set_glitch_filter(GPIO_MARK_PIN, 10000)
pi.set_glitch_filter(GPIO_NEXT_PIN, 10000)
pi.set_glitch_filter(GPIO_TIMER_PIN, 10000)

class Timer:
  def __init__(self, func, tick):
    self.completed = False
    self.func = func
    self.tick = tick
    self.running = False

  def start(self, time):
    self.time = time
    self.thread = Thread(target=self.run)
    self.running = True
    self.completed = False
    self.thread.start()

  def stop(self):
    self.running = False

  def run(self):
    while(not self.completed and self.running):
      time.sleep(1)
      if(self.tick != None): self.tick(self.time)
      self.time = self.time - 1
      if(self.time <= 0):
        self.running = False
        self.completed = True
        if(self.func != None): self.func()

def pomodoro_tick(remaining_time):
    global pomodoro_remaining_time
    pomodoro_remaining_time = remaining_time

def pomodoro_finish():
    global timer_finished
    timer_finished = False
    time.sleep(2)

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((20, 30), "TIMER FINISHED", fill="white")

    global pomodoro_remaining_time
    pomodoro_remaining_time = POMODORO_TIME

    time.sleep(4)
    timer_finished = True

current_todo_id = -1
pomodoro_remaining_time = POMODORO_TIME
timer_finished = True

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

timer = Timer(pomodoro_finish, pomodoro_tick)

def timeToClock(time):
  mins = int((time - time % 60) / 60)
  secs = int(time % 60)
  return '%d:%d'%(mins, secs)

def oled_screen():
    while (True):
        if(not timer_finished): continue
        time.sleep(0.1)

        current_todo = get_current_todo()

        with canvas(device) as draw:
            if(current_todo == None):
       	        draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text(TODO_TEXT_LINE_INDICES[0], "No todos yet", fill="white")
                draw.text(POMODORO_TIMER_LINE_INDEX, timeToClock(pomodoro_remaining_time), fill="white")

            else:
                todo_lines = get_todo_text_lines(current_todo)

       	        draw.rectangle(device.bounding_box, outline="white", fill="black")
                draw.text(TODO_TEXT_LINE_INDICES[0], todo_lines[0], fill="white")
                draw.text(TODO_TEXT_LINE_INDICES[1], todo_lines[1], fill="white")
                draw.text(TODO_TEXT_LINE_INDICES[2], todo_lines[2], fill="white")
                draw.text(TODO_TEXT_LINE_INDICES[3], todo_lines[3], fill="white")
                if(current_todo['duedate'] != None):
                    draw.text(TODO_DUEDATE_LINE_INDEX, current_todo['duedate'], fill="white")
                draw.text(POMODORO_TIMER_LINE_INDEX, timeToClock(pomodoro_remaining_time), fill="white")

def get_current_todo(todos = None):
    global current_todo_id
    if(todos == None):
        todos = get_todos()

    if(len(todos) == 0): return None
    if(current_todo_id == -1):
        current_todo_id = todos[0]['id']

    found_todo = None
    try:
        found_todo = [todo for todo in todos if todo['id'] == current_todo_id][0]
    except: pass
    if(found_todo == None and current_todo_id != -1):
        current_todo_id = -1
        return get_current_todo()

    return found_todo

def get_todos():
    todos = requests.get(API_URL).json()
    todos = [todo for todo in todos if todo['isCompleted'] == 0]
    return todos

def get_todo_text_lines(todo):
    result = [
        todo['text'][0 : MAX_CHAR_ON_LINE].strip(),
        todo['text'][MAX_CHAR_ON_LINE : MAX_CHAR_ON_LINE * 2].strip(),
        todo['text'][MAX_CHAR_ON_LINE * 2 : MAX_CHAR_ON_LINE * 3].strip(),
        todo['text'][MAX_CHAR_ON_LINE * 3 : MAX_CHAR_ON_LINE * 4].strip()
    ]

    return result

def button_press(pin, level, tick):
    global current_todo_id
    if(pin == GPIO_MARK_PIN):
        try:
            requests.put(API_URL, json=current_todo_id)
            current_todo_id = -1
        except: pass
            

    elif(pin == GPIO_NEXT_PIN):
        try:
            todos = get_todos()
            todo = get_current_todo(todos)
            index = todos.index(todo)
            nextTodo = todos[(index + 1) % len(todos)]
            current_todo_id = nextTodo['id']
        except: pass

    elif(pin == GPIO_PREV_PIN):
        try:
            todos = get_todos()
            todo = get_current_todo(todos)
            index = todos.index(todo)
            prevTodo = todos[(index - 1) % len(todos)]
            current_todo_id = prevTodo['id']
        except: pass

    elif(pin == GPIO_TIMER_PIN):
        global pomodoro_remaining_time
        if(not timer.running): timer.start(pomodoro_remaining_time)
        else:
            timer.stop()
            time.sleep(1)
            pomodoro_remaining_time = POMODORO_TIME

pi.callback(GPIO_PREV_PIN, pigpio.FALLING_EDGE, button_press)
pi.callback(GPIO_MARK_PIN, pigpio.FALLING_EDGE, button_press)
pi.callback(GPIO_NEXT_PIN, pigpio.FALLING_EDGE, button_press)
pi.callback(GPIO_TIMER_PIN, pigpio.FALLING_EDGE, button_press)

if(__name__ == '__main__'):
    oled_screen()
