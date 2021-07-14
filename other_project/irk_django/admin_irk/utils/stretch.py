# -*- coding: utf-8 -*-

"""
Процессор для sorl-thumbnail, который дополняет по ширине изображение заблюренным фоном.
Сначала растягивает изображение до чуть больше нужной ширины, потом блюрит его,
потом обрезает до нужных размеров и в конце концов делает подложкой с оригинальным.
"""

from PIL import ImageFilter


def stretch_thumbnail_processor(image, requested_size, opts):

    if requested_size[0] > image.size[0] and 'stretch' in opts:
        ratio = float(requested_size[0])/image.size[0]
        width = requested_size[0]
        height = int(requested_size[1]*ratio)
        bg_image = image.resize((width+10, height))

        for i in range(20):
            bg_image = bg_image.filter(ImageFilter.BLUR)

        height_diff = int(float(bg_image.size[1] - image.size[1])/2)
        if height_diff > 0:
            box = (5, height_diff, bg_image.size[0]-5, bg_image.size[1]-height_diff)
            bg_image = bg_image.crop(box)

        bg_image.paste(image, 
                       (int(float(bg_image.size[0]-image.size[0])/2), 
                        int(float(bg_image.size[1]-image.size[1])/2)))
        return bg_image

    return image
stretch_thumbnail_processor.valid_options = ['stretch']
