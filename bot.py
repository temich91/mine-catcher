import pyautogui as pag
import cv2
import numpy as np
from PIL import Image
import imagehash

TEMPLATES_FILENAMES = [
    "templates/unsolved.png",
    "templates/0.png",
    "templates/1.png",
    "templates/2.png",
    "templates/3.png",
    "templates/4.png",
    "templates/5.png",
    "templates/6.png",
    "templates/7.png",
    "templates/8.png",
    "templates/mine.png",
    "templates/flag.png"
]

PHASH_THRESHOLD = 10

CELL_SYMBOLS = {
    "unsolved": ".",
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "mine": "*",
    "flag": "F"
}


class Bot:
    def __init__(self):
        self.field = None
        self.field_image = None
        self.width = None
        self.height = None

        self.get_field_image()
        self.initialize_field()

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
        try:
            pag.locateOnScreen("templates/triggered_mine.png", confidence=0.95)
        except pag.ImageNotFoundException:
            return False
        return True

    def get_cell_symbol(self, img, templ):
        template = cv2.imread(templ)
        template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
        template = Image.fromarray(template)
        template_hash = imagehash.phash(template)

        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image_hash = imagehash.phash(image)

        if template_hash - image_hash > PHASH_THRESHOLD:
            return False

        cell_name = templ[templ.find("/") + 1: templ.find(".")]
        return CELL_SYMBOLS[cell_name]

    def get_field_image(self):
        ul, br = self.find_field()
        if not ul:
            return

        field_screenshot = pag.screenshot(region=(ul[0], ul[1], br[0] - ul[0], br[1] - ul[1])) #x, y, width, height
        self.field_image = np.asarray(field_screenshot)

    def initialize_field(self):
        height, width = self.field_image.shape[:2]
        self.width = (width + 3) // 24
        self.height = (height + 3) // 24
        self.field = [["?" for _ in range(self.width)] for __ in range(self.height)]

    def scan_field(self):
        if self.check_game_state():
            print("Game over.")
            return

        for y in range(self.height):
            for x in range(self.width):
                cell = self.field_image[x * 24: x * 24 + 21,
                                        y * 24: y * 24 + 21]
                for templ_path in TEMPLATES_FILENAMES:
                    symbol = self.get_cell_symbol(cell, templ_path)
                    if symbol:
                        self.field[x][y] = symbol
                        break

bot = Bot()
bot.scan_field()
f = bot.field
for i in f:
    print(*i)
