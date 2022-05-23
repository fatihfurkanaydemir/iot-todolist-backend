from threading import Thread
import time

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