import io
import os
import xml.etree.ElementTree as ET
from copy import deepcopy

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


class MapGenerator:
    def __init__(self, regions, map_size):
        self.svg = ET.parse(os.path.join(os.path.dirname(__file__), 'ua.svg'))
        self.svg_red = deepcopy(self.svg)
        self.regions = regions
        self.size = map_size

    def generate_map(self):
        self.fill_bw_map()
        self.fill_red_map()

        img_bw = self.form_map_image(self.svg)
        img_red = self.form_map_image(self.svg_red)

        return img_bw, img_red

    def fill_bw_map(self):
        for region in self.regions:
            elements = self.svg.findall(f'.//*[@name="{region}"]')
            for element in elements:
                element.set("stroke-width", "1")

                if self.regions[region] == "partial":
                    element.set("fill", "#FF0000")
                elif self.regions[region] == "no_data":
                    element.set("fill", "#AA0000")

    def fill_red_map(self):
        for region in self.regions:
            elements = self.svg_red.findall(f'.//*[@name="{region}"]')
            for element in elements:
                if self.regions[region] == "full":
                    element.set("fill", "#000000")
                element.set("stroke-opacity", "0")
                element.set("stroke-width", "0")
                # element.set("stroke", "#FFFFFF")

    def form_map_image(self, svg):
        xmlstr = ET.tostring(svg.getroot(), encoding='utf8', method='xml').decode("utf-8")
        img = self.render_svg(xmlstr, 1)\
            .convert('1', dither=True)\
            .resize(self.size)

        return img

    @staticmethod
    def render_svg(_svg, _scale):
        drawing = svg2rlg(io.BytesIO(bytes(_svg, 'utf-8')))
        return renderPM.drawToPIL(drawing)
