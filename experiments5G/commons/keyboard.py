# import getch
from concurrent.futures import thread
import threading
import time
from getkey import getkey

class KeypressDetector:
    def __init__(self, keychar='s'):
        self.pressed = False
        self.keychar = keychar
        self.t = threading.Thread(target=self.run)
        self.t.start()

    def run(self):
        while True:
            if not self.pressed:
                x = getkey()
                if x == self.keychar:
                    self.pressed = True

    def was_pressed(self):
        return self.pressed
    
    def reset(self):
        self.pressed = False

if __name__ == "__main__":
    o = KeypressDetector()
    while True:
        if o.was_pressed():
            print("key was pressed!")
            o.reset()
        time.sleep(0.1)
