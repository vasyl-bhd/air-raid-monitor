import logging

from PIL import Image
from waveshare_epd import epd5in83b_V2

from epd.eink_renderer import EinkRenderer


class Eink(EinkRenderer):

    def __init__(self):
        self.epd = self.init_display()

    @staticmethod
    def clear_display(epd=None):
        if epd is None:
            epd = epd5in83b_V2.EPD()
        epd.Clear()

    @staticmethod
    def init_display():
        logging.info("Initializing display")

        epd = epd5in83b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        Eink.clear_display(epd)
        logging.info("init and Clear finished")
        return epd

    def get_dimensions(self) -> (int, int):
        return self.epd.width, self.epd.height

    def render(self, img_bw: Image, img_red: Image):
        logging.info("Updating screen")
        screen_image_rotated = img_bw.rotate(180)
        screen_image_red_rotated = img_red.rotate(180)

        self.epd.display(self.epd.getbuffer(screen_image_rotated), self.epd.getbuffer(screen_image_red_rotated))

    @staticmethod
    def close():
        logging.info("Clearing display")
        Eink.clear_display()
        logging.info("Exiting module")
        epd5in83b_V2.epdconfig.module_exit()
