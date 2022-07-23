import os
import xml.etree.ElementTree as ET
import io
from collections import Counter

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image, ImageDraw, ImageFont
from observer import Observer
from waveshare_epd import epd5in83b_V2
import logging

FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), 'Monaco.ttf'), 18)

MAP_SIZE = (500, 350)

class Eink(Observer):

    def __init__(self, observable):
        super().__init__(observable=observable)
        self.epd = self._init_display()
        self.screen_image_bw = Image.new('1', (self.epd.width, self.epd.height), 255)
        self.screen_image_red = Image.new('1', (self.epd.width, self.epd.height), 255)
        self.screen_draw = ImageDraw.Draw(self.screen_image_bw)

    @staticmethod
    def _init_display():
        logging.info("Initializing display")

        epd = epd5in83b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        logging.info("init and Clear finished")
        return epd

    def update(self, data):
        logging.info("Updating screen")
        self.form_image(data, self.screen_draw, self.screen_image_bw)

        logging.info("Formed image")
        screen_image_rotated = self.screen_image_bw.rotate(180)
        self.epd.display(self.epd.getbuffer(screen_image_rotated), self.epd.getbuffer(screen_image_rotated))

    def close(self):
        epd5in83b_V2.epdconfig.module_exit()

    def form_image(self, regions, screen_draw, image):
        def pos(x, y):
            side = 14
            return [(x, y), (x + side, y + side)]

        screen_draw.rectangle((0, 0, self.epd.width, self.epd.height), fill="#ffffff")

        if not regions:
            self.connection_lost_text(screen_draw)
            return

        map = self.generate_map(regions)
        image.paste(map, (self.epd.width - MAP_SIZE[0], 0))
        self.text(screen_draw)
        self.legend(image, pos, regions, screen_draw)

    def legend(self, image, pos, regions, screen_draw):
        tmp = Image.new('RGB', (15, 15), "#FFFFFF")
        ImageDraw.Draw(tmp).rounded_rectangle(pos(0, 0), 3, fill="#FF0000", outline="#000000")
        tmp = tmp.convert('1', dither=True)
        counter = Counter(regions.values())
        screen_draw.rounded_rectangle(pos(1, 106), 3, fill="#FFFFFF", outline="#000000")
        screen_draw.text((20, 108), "nothing - %d" % counter[None], font=FONT_SMALL)
        image.paste(tmp, (1, 90))
        screen_draw.text((20, 92), "partial - %d" % counter['partial'], font=FONT_SMALL)
        screen_draw.rounded_rectangle(pos(1, 74), 3, fill="#000000")
        screen_draw.text((20, 76), "full - %d" % counter['full'], font=FONT_SMALL)

    def text(self, screen_draw):
        screen_draw.text((16, 4), "Air raid", font=FONT_SMALL)
        screen_draw.text((12, 16), "sirens in", font=FONT_SMALL)
        screen_draw.text((12, 28), " Ukraine", font=FONT_SMALL)

    def connection_lost_text(self, screen_draw):
        screen_draw.text((self.epd.width / 2, self.epd.width / 2), 'NO CONNECTION', font=FONT_SMALL)

    @staticmethod
    def render_svg(_svg, _scale):
        drawing = svg2rlg(io.BytesIO(bytes(_svg, 'utf-8')))
        return renderPM.drawToPIL(drawing)

    def generate_map(self, regions):
        tree = ET.parse(os.path.join(os.path.dirname(__file__), 'ua.svg'))
        for region in regions:
            elements = tree.findall(f'.//*[@name="{region}"]')
            for element in elements:
                if regions[region] == "full":
                    element.set("fill", "#000000")
                elif regions[region] == "partial":
                    element.set("fill", "#FF0000")
                elif regions[region] == "no_data":
                    element.set("fill", "#AA0000")
        xmlstr = ET.tostring(tree.getroot(), encoding='utf8', method='xml').decode("utf-8")
        img = Eink.render_svg(xmlstr, 1)
        img = img.convert('1', dither=True)
        img = img.resize(MAP_SIZE)
        return img

    def show_all(self):
        elements = self.tree.findall(".//*[@name]")
        for element in elements:
            print(element.get("name"))
