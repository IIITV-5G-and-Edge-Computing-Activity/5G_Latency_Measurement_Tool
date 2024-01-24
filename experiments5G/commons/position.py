from typing import Tuple
import time
import random

# https://stackoverflow.com/questions/18636564/lat-long-or-long-lat
# ISO 6709
# order (lat, long) or (y,x)
# Lat = Y Long = X


class PosBase:
    def __init__(self, initial_coords: tuple):
        self.current_coords = initial_coords

    def get_current_pos(self) -> Tuple[Tuple[float, float], dict]:
        """
        Returns tuple (latitude, longitude) + Dict (with cache values that may be relevenat later)
        """
        return self.current_coords, {}


class RosGpsPos(PosBase):
    def __init__(self, initial_coords, topic="/gps/filtered"):
        super().__init__(initial_coords)
        import rospy
        from sensor_msgs.msg import NavSatFix
        x = self.current_coords

        def gps_callback(data):
            nonlocal x
            rospy.loginfo("New coordinates: {}, {}".format(str(data.latitude), str(data.longitude)))
            x = (data.latitude, data.longitude)
            self.current_coords = x

        rospy.init_node('gps_listener', anonymous=True)
        rospy.Subscriber(topic, NavSatFix, gps_callback)


def try_repeat(fn):
    while True:
        try:
            x = fn()
            return x
        except Exception as e:
            print(f"Caught Exception: {e}; Try again ...")

            #  get_x_fn=lambda: float(input("Enter X:")),
            #  get_y_fn=lambda: float(input("Enter Y:"))):


class ManualPos(PosBase):
    def __init__(self,
                 keychar="s",
                 landmark_x_to_x_fn=lambda x: x,
                 landmark_y_to_y_fn=lambda y: y,
                 landmark_x_name="X",
                 landmark_y_name="Y"):
        self.landmark_x_name = landmark_x_name
        self.landmark_y_name = landmark_y_name
        self.landmark_x_fn = lambda: float(input(f"Enter {landmark_x_name}: "))
        self.landmark_y_fn = lambda: float(input(f"Enter {landmark_y_name}: "))
        self.landmark_x_to_x_fn = landmark_x_to_x_fn
        self.landmark_y_to_y_fn = landmark_y_to_y_fn
        self.keychar = keychar
        # super().__init__()
        from experiments5G.commons.keyboard import KeypressDetector
        self.update_vals()
        self.k = KeypressDetector(keychar)

    def update_vals(self):
        landmark_x = try_repeat(self.landmark_x_fn)
        landmark_y = try_repeat(self.landmark_y_fn)
        x = self.landmark_x_to_x_fn(landmark_x)
        y = self.landmark_y_to_y_fn(landmark_y)
        self.current_coords = (y, x)
        self.current_cache = {self.landmark_x_name: landmark_x, self.landmark_y_name: landmark_y}

    def get_current_pos(self):
        if self.k.was_pressed():
            print(f"Press key '{self.keychar}' to enter a new position.")
            self.update_vals()
            self.k.reset()
        return self.current_coords, self.current_cache


class RandomPos(PosBase):
    def __init__(self, y1, y2, x1, x2):
        y_diff = y2 - y1
        x_diff = x2 - x1
        self.y_fn = lambda: random.random() * y_diff + y1
        self.x_fn = lambda: random.random() * x_diff + x1
        super().__init__(self.get_current_pos())

    def get_current_pos(self):
        return (self.y_fn(), self.x_fn()), {}


if __name__ == "__main__":
    x = ManualPos((0, 0))
    while True:
        # print("test")
        print(x.get_current_pos())
        time.sleep(0.4)
