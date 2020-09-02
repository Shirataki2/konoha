import unicodedata
import discord
import re
from PIL import Image, ImageDraw, ImageFont


def user_reaction_check(message, emojis, ctx):
    return lambda r, m: all([r.message.id == message.id, m == ctx.author, r.emoji in emojis])


def unicodelen(t):
    text_counter = 0
    for c in t:
        j = unicodedata.east_asian_width(c)
        if 'F' == j:
            text_counter = text_counter + 2
        elif 'H' == j:
            text_counter = text_counter + 1
        elif 'W' == j:
            text_counter = text_counter + 2
        elif 'Na' == j:
            text_counter = text_counter + 1
        elif 'A' == j:
            text_counter = text_counter + 2
        else:
            text_counter = text_counter + 1
    return text_counter


class TextImageGenerator:
    def __init__(self, font, text, image_size=128, fg_color=(255, 0, 0, 255), bg_color=(255, 255, 255, 0), offset=0):
        self.font = font
        self.image_size = image_size
        self.offset = offset
        text = re.sub(";+", ";", text)
        self.texts = text.split(";")
        self.lines = len(self.texts)
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.img = Image.new(
            "RGBA", (self.image_size, self.image_size), bg_color)

    def render(self):
        for i, text in enumerate(self.texts):
            fnt = ImageFont.truetype(self.font, self.image_size)
            sz = fnt.getsize(text)
            img = Image.new("RGBA", sz, self.bg_color)
            draw = ImageDraw.Draw(img)
            draw.text((0, -self.offset), text, font=fnt,
                      fill=self.fg_color, align='center')
            img = img.resize(
                (self.image_size, self.image_size // self.lines + self.offset // self.lines))
            self.img.paste(img, (0, i * (self.image_size // self.lines)))
        return self.img
