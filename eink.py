import os
import xml.etree.ElementTree as ET

from collections import Counter

from PIL import Image, ImageDraw, ImageFont

from MapGenerator import MapGenerator
from observer import Observer
from waveshare_epd import epd5in83b_V2
import logging

FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), 'Monaco.ttf'), 18)

MAP_SIZE = (500, 350)


class Eink(Observer):

    def __init__(self, observable):
        super().__init__(observable=observable)
        self.epd = self.init_display()
        self.epd_middle_width = self.epd.width / 2
        self.epd_middle_height = self.epd.height / 2
        self.screen_image_bw = Image.new('1', (self.epd.width, self.epd.height), 255)
        self.screen_image_red = Image.new('1', (self.epd.width, self.epd.height), 255)
        self.screen_draw_bw = ImageDraw.Draw(self.screen_image_bw)
        self.screen_draw_red = ImageDraw.Draw(self.screen_image_red)

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

    def update(self, data):
        logging.info("Updating screen")
        self.form_image(data)

        logging.info("Formed image")
        screen_image_rotated = self.screen_image_bw.rotate(180)
        screen_image_red_rotated = self.screen_image_red.rotate(180)
        self.epd.display(self.epd.getbuffer(screen_image_rotated), self.epd.getbuffer(screen_image_red_rotated))

    @staticmethod
    def close():
        Eink.clear_display()
        epd5in83b_V2.epdconfig.module_exit()

    def form_image(self, regions):
        def pos(x, y):
            side = 14
            return [(x, y), (x + side, y + side)]

        self.screen_draw_bw.rectangle((0, 0, self.epd.width, self.epd.height), fill="#ffffff")

        if not regions:
            self.connection_lost_text()
            return

        air_raid_map = MapGenerator(regions=regions, map_size=MAP_SIZE).generate_map()

        self.screen_image_bw.paste(air_raid_map[0], (self.epd.width - MAP_SIZE[0], 0))
        self.screen_image_red.paste(air_raid_map[1], (self.epd.width - MAP_SIZE[0], 0))
        self.draw_text()
        self.legend(pos, regions)

    def legend(self, pos, regions):
        counter = Counter(regions.values())

        self.screen_draw_red.rounded_rectangle(pos(1, 74), 3, fill=0)
        self.screen_draw_bw.text((20, 76), "full - %d" % counter['full'], font=FONT_SMALL)

        tmp = Image.new('RGB', (15, 15), "#FFFFFF")
        ImageDraw.Draw(tmp).rounded_rectangle(pos(0, 0), 3, fill="#FF0000", outline="#000000")
        tmp = tmp.convert('1', dither=True)
        self.screen_image_bw.paste(tmp, (1, 90))
        self.screen_draw_bw.text((20, 92), "partial - %d" % counter['partial'], font=FONT_SMALL)

        self.screen_draw_bw.rounded_rectangle(pos(1, 106), 3, fill="#FFFFFF", outline="#000000")
        self.screen_draw_bw.text((20, 108), "nothing - %d" % counter[None], font=FONT_SMALL)

    def draw_text(self):
        self.screen_draw_bw.text((16, self.epd_middle_height + 104), "Air raid", font=FONT_SMALL)
        self.screen_draw_bw.text((12, self.epd_middle_height + 120), "sirens in", font=FONT_SMALL)
        self.screen_draw_bw.text((12, self.epd_middle_height + 136), " Ukraine", font=FONT_SMALL)

    def connection_lost_text(self):
        self.screen_draw_bw.text((self.epd.width / 2, self.epd.width / 2), 'NO CONNECTION', font=FONT_SMALL)

    def show_all(self):
        elements = self.tree.findall(".//*[@name]")
        for element in elements:
            print(element.get("name"))
