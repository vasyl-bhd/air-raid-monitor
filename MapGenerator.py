import io
import os
import xml.etree.ElementTree as ET
from copy import deepcopy

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


class MapGenerator:
    def __init__(self, regions, map_size):
        self.svg = ET.parse(os.path.join(os.path.dirname(__file__), 'ua.svg'))
        self.red_svg = deepcopy(self.svg)
        self.regions = regions
        self.size = map_size

    def generate_map(self):
        for region in self.regions:
            elements = self.svg.findall(f'.//*[@name="{region}"]')
            for element in elements:
                if self.red_svg[region] == "full":
                    element.set("fill", "#FF0000")
                elif self.svg[region] == "partial":
                    element.set("fill", "#000000")
                elif self.svg[region] == "no_data":
                    element.set("fill", "#AA0000")
        bw_xmlstr = ET.tostring(self.svg.getroot(), encoding='utf8', method='xml').decode("utf-8")
        red_xmlstr = ET.tostring(self.red_svg.getroot(), encoding='utf8', method='xml').decode("utf-8")
        img_bw = self.render_svg(bw_xmlstr, 1)
        img_bw = img_bw.convert('1', dither=True)
        img_bw = img_bw.resize(self.size)

        img_red = self.render_svg(red_xmlstr, 1)
        img_red = img_red.convert('1', dither=True)
        img_red = img_red.resize(self.size)

        return img_bw, img_red

    @staticmethod
    def render_svg(_svg, _scale):
        drawing = svg2rlg(io.BytesIO(bytes(_svg, 'utf-8')))
        return renderPM.drawToPIL(drawing)
