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
IMAGE_LOCATION_CONFIDENCE = 0.99
TOP_LEFT_CORNER_SHIFT_X = 20
TOP_LEFT_CORNER_SHIFT_Y = 26

BOTTOM_RIGHT_CORNER_SHIFT_X = 9
BOTTOM_RIGHT_CORNER_SHIFT_Y = -1

CELLS_DIST = 24
CELL_SIDE_SIZE = 21
CELL_CENTER_SHIFT = 10

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

    def get_corner_coords(self, image_name, x_shift, y_shift):
        try:
            corner = list(pag.locateOnScreen(f"templates/{image_name}.png", confidence=IMAGE_LOCATION_CONFIDENCE))
            corner = list(map(int, corner))
            corner[0] += x_shift
            corner[1] += y_shift
            return corner[0], corner[1]

        except pag.ImageNotFoundException:
            return False, False

    def find_field(self):
        ul_corner = self.get_corner_coords("top_left_corner", TOP_LEFT_CORNER_SHIFT_X, TOP_LEFT_CORNER_SHIFT_Y)
        br_corner = self.get_corner_coords("bottom_right_corner_unsolved", BOTTOM_RIGHT_CORNER_SHIFT_X, BOTTOM_RIGHT_CORNER_SHIFT_Y) or \
                    self.get_corner_coords("bottom_right_corner", BOTTOM_RIGHT_CORNER_SHIFT_X, BOTTOM_RIGHT_CORNER_SHIFT_Y)
        pag.moveTo(br_corner[0], br_corner[1])

        return ul_corner, br_corner

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

        if not (ul[0] and br[0]):
            print("Game was not found. Сheck if the field is on the main screen and if it is fully positioned.")
            return

        field_screenshot = pag.screenshot(region=(ul[0], ul[1], br[0] - ul[0], br[1] - ul[1])) #x, y, width, height
        self.field_image = np.asarray(field_screenshot)

    def initialize_field(self):
        if self.field_image is None:
            return
        height, width = self.field_image.shape[:2]
        self.width = (width + 3) // 24
        self.height = (height + 3) // 24
        self.field = [["?" for _ in range(self.width + 2)] for __ in range(self.height + 2)]

    def scan_field(self):
        if self.field_image is None:
            return

        if self.check_game_state():
            print("Game over.")
            return

        # --------> x
        # |
        # |
        # |
        # V
        # y

        corner_cell_x, corner_cell_y = self.get_corner_coords("top_left_corner", 20 + CELL_CENTER_SHIFT,
                                                              26 + CELL_CENTER_SHIFT)
        for h in range(self.height):
            for w in range(self.width):
                cell = self.field_image[h * CELLS_DIST: h * CELLS_DIST + CELL_SIDE_SIZE,
                                        w * CELLS_DIST: w * CELLS_DIST + CELL_SIDE_SIZE]
                for templ_path in TEMPLATES_FILENAMES:
                    symbol = self.get_cell_symbol(cell, templ_path)
                    if symbol:
                        if symbol == "F":
                            pag.rightClick(corner_cell_x + w * CELLS_DIST, corner_cell_y + h * CELLS_DIST)
                            symbol = "."
                        self.field[h + 1][w + 1] = symbol
                        break

    def move(self):
        bot.scan_field()
        corner_cell_x, corner_cell_y = self.get_corner_coords("top_left_corner", 20, 26)
        corner_cell_x += CELL_CENTER_SHIFT
        corner_cell_y += CELL_CENTER_SHIFT
        for y in range(self.height):
            for x in range(self.width):
                pass

    def find_unsolved_neighbours(self, x, y):
        unsolved_neighbours = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                if self.field[x + i][y + j] == ".":
                    unsolved_neighbours.add((x + i, y + j))
        return unsolved_neighbours

    def find_edge_cells(self):
        bot.scan_field()
        corner_cell_x, corner_cell_y = self.get_corner_coords("top_left_corner", TOP_LEFT_CORNER_SHIFT_X, TOP_LEFT_CORNER_SHIFT_Y)
        corner_cell_x += CELL_CENTER_SHIFT
        corner_cell_y += CELL_CENTER_SHIFT

        edge_cells = set()
        for h in range(1, self.height + 1):
            for w in range(1, self.width + 1):
                if self.field[h][w].isdigit():
                    edge_cells = edge_cells.union(self.find_unsolved_neighbours(h, w))

        print(sorted(edge_cells))


    def calculate_safe_probability(self):
        pass

bot = Bot()
bot.find_edge_cells()
# bot.move()
# bot.scan_field()
for i in bot.field:
    print(*i)
