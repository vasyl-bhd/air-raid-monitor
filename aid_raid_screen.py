import os
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

from MapGenerator import MapGenerator
from epd.eink_renderer import EinkRenderer
from observer import Observer

MAP_OFFSET = (140, 130)
FONT_SMALL = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), 'Monaco.ttf'), 18)


class AirRaidScreen(Observer):

    def __init__(self, observable, eink_renderer: EinkRenderer):
        super().__init__(observable=observable)

        self.eink_renderer = eink_renderer

        dimensions = eink_renderer.get_dimensions()
        self.screen_width = dimensions[0]
        self.screen_height = dimensions[1]

        self.screen_middle_width = self.screen_width // 2
        self.screen_middle_height = self.screen_height // 2

        self.map_size = (self.screen_width - MAP_OFFSET[0], self.screen_height - MAP_OFFSET[1])

        self.screen_image_bw = Image.new('1', (self.screen_width, self.screen_height), 255)
        self.screen_image_red = Image.new('1', (self.screen_width, self.screen_height), 255)

        self.screen_draw_bw = ImageDraw.Draw(self.screen_image_bw)
        self.screen_draw_red = ImageDraw.Draw(self.screen_image_red)

    def form_image(self, regions):
        self.screen_draw_bw.rectangle((0, 0, self.screen_width, self.screen_height), fill="#ffffff")

        if not regions:
            self.connection_lost_text()
            return

        air_raid_map = MapGenerator(regions=regions, map_size=self.map_size).generate_map()

        self.screen_image_bw.paste(air_raid_map[0], (self.screen_width - self.map_size[0], 0))
        self.screen_image_red.paste(air_raid_map[1], (self.screen_width - self.map_size[0], 0))
        self.draw_text()
        self.legend(regions)

        return self.screen_image_bw, self.screen_image_red

    def legend(self, regions):
        counter = Counter(regions.values())
        legend_full_stats_height = self.screen_middle_height + 54
        legend_partial_stats_height = self.screen_middle_height + 70
        legend_no_data_stats_height = self.screen_middle_height + 86

        def pos(coords):
            x, y = coords
            side = 14
            return [(x, y), (x + side, y + side)]

        def icon_pos(height):
            return 1, height

        def text_pos(height):
            return 20, height

        self.screen_draw_red.rounded_rectangle(pos(icon_pos(legend_full_stats_height)), 3, fill=0)
        self.screen_draw_bw.text(text_pos(legend_full_stats_height), "full - %d" % counter['full'], font=FONT_SMALL)

        tmp = Image.new('RGB', (15, 15), "#FFFFFF")
        ImageDraw.Draw(tmp).rounded_rectangle(pos((0, 0)), 3, fill="#FF0000", outline="#000000")
        tmp = tmp.convert('1', dither=True)
        self.screen_image_bw.paste(tmp, icon_pos(legend_partial_stats_height))
        self.screen_draw_bw.text(text_pos(legend_partial_stats_height), "partial - %d" % counter['partial'],
                                 font=FONT_SMALL)

        self.screen_draw_bw.rounded_rectangle(pos(icon_pos(legend_no_data_stats_height)), 3, fill="#FFFFFF",
                                              outline="#000000")
        self.screen_draw_bw.text(text_pos(legend_no_data_stats_height), "nothing - %d" % counter[None], font=FONT_SMALL)

    def draw_text(self):
        self.screen_draw_bw.text((16, 50), "Air raid", font=FONT_SMALL)
        self.screen_draw_bw.text((12, 66), "sirens in", font=FONT_SMALL)
        self.screen_draw_bw.text((12, 82), " Ukraine", font=FONT_SMALL)

        self.screen_draw_bw.text((self.screen_middle_width + 100, self.screen_middle_height + 182), "I <3 Ann",
                                 font=FONT_SMALL)

    def connection_lost_text(self):
        self.screen_draw_bw.text((self.screen_middle_width, self.screen_middle_height), 'NO CONNECTION',
                                 font=FONT_SMALL)

    def update(self, data):
        bw, red = self.form_image(regions=data)
        self.eink_renderer.render(bw, red)
