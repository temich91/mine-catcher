import pyautogui as pag
import cv2


class Bot:
    def __init__(self):
        pass

    def find_field(self):
        try:
            ul_corner = list(pag.locateOnScreen("templates/top_left_corner.png", confidence=0.99))
            ul_corner = list(map(int, ul_corner))

            ul_corner[0] += 19
            ul_corner[1] += 24

            br_corner = list(pag.locateOnScreen("templates/bottom_right_corner.png"))
            br_corner = list(map(int, br_corner))

            br_corner[0] += 12
            br_corner[1] += -4

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


bot = Bot()
bot.get_field_image()
