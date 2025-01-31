import pyautogui as pag
import cv2
import numpy as np


class Bot:
    def __init__(self):
        self.field = None
        self.field_image = None
        self.width = None
        self.height = None

        self.get_field_image()
        self.get_field_size()

    def find_field(self):
        try:
            ul_corner = list(pag.locateOnScreen("templates/top_left_corner.png", confidence=0.99))
            ul_corner = list(map(int, ul_corner))

            ul_corner[0] += 20
            ul_corner[1] += 26

            br_corner = list(pag.locateOnScreen("templates/bottom_right_corner.png"))
            br_corner = list(map(int, br_corner))

            br_corner[0] += 13
            br_corner[1] += -2

            return ul_corner, br_corner

        except pag.ImageNotFoundException:
            print("Game was not found. Сheck if the field is on the main screen and if it is fully positioned.")
            return False, False

    def check_game_state(self):
        pass

    def get_field_image(self):
        ul, br = self.find_field()
        if not ul:
            return

        pag.screenshot("field.png", region=(ul[0], ul[1], br[0] - ul[0], br[1] - ul[1])) #x, y, width, height
        self.field_image = np.asarray(cv2.imread("field.png"))

    def get_field_size(self):
        width, height = self.field_image.shape[:2]
        self.width = (width + 3) // 24
        self.height = (height + 3) // 24

    def scan_field(self):
        cnt = 0
        template = np.asarray(cv2.imread("templates/3.png"))
        for x in range(self.width):
            for y in range(self.height):
                cell = self.field_image[x * 21: x * 21 + 21,
                                        y * 21: y * 21 + 21]

                cell = np.asarray(cell)
                if (cell == template).all():
                    cnt += 1
        print(cnt)


bot = Bot()
bot.scan_field()
