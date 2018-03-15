
import math
from PIL import Image

GRAY_SCALE_PALETTE = [(_ // 3) * 16 for _ in range(16*3)]


class ImageFormatError(Exception):
    pass


def has_valid_size(img):
    w, h = img.size
    return h % 8 == 0 and w % 8 == 0


def validate_gbaimage(img):
    if img.mode != 'P':
        raise ImageFormatError('Image is not indexed')
    if not has_valid_size(img):
        raise ImageFormatError('Image\'s height and width must be multiple of 8')


def format_palette(palette, colors=16):
    formated = [[255, 255, 255]] * colors
    for i in range(colors):
        formated[i] = palette[i * 3: (i + 1) * 3]
    return formated


def from_img_to_4bpp(img):
    validate_gbaimage(img)
    data = b''
    imgdata = img.getdata()
    w, h = img.size
    tiles_h, tiles_w = h // 8, w // 8
    for tile in range(tiles_h * tiles_w):
        tile_data = b''
        index = 8 * (tile % tiles_w) + w * 8 * (tile // tiles_w)
        for j in range(8):
            for i in range(4):
                n = (imgdata[index + 2*i + j*w] & 0xf) | ((imgdata[index + 2*i + j*w + 1] & 0xf) << 4)
                tile_data += n.to_bytes(1, 'little')

        data += tile_data
    return data


def img_palette_to_gba(img):
    return palette_to_gba(img.getpalette())


def palette_to_gba(palette):
    formatted = format_palette(palette)
    return pal_to_gba(formatted)


def pal_to_gba(palette):
    data = b''
    for color in palette:
        r, g, b = color
        r >>= 3
        g >>= 3
        b >>= 3
        data += (r | (g << 5) | (b << 10)).to_bytes(2, 'little')
    return data


def from_gba_to_pal(data):
    pal_list = []

    for i in range(len(data) // 2):
        n = int.from_bytes(data[i * 2:(i + 1) * 2], 'little')
        r = (n & 0x1f) << 3
        g = (n & 0x3e0) >> 2
        b = (n & 0x7c00) >> 7
        pal_list.extend((r, g, b))

    return pal_list


def from_4bpp_to_img(gbadata, tiles_wide):
    total_tiles = len(gbadata) // 32
    tiles_high = math.ceil(total_tiles / tiles_wide)

    img_data = [0] * (64 * tiles_wide * tiles_high)

    for i in range(len(gbadata)):
        pixel_pair = gbadata[i]
        pixel_1 = pixel_pair & 0xf
        pixel_2 = pixel_pair >> 4

        tile_x = (i >> 5) % tiles_wide
        tile_y = (i >> 5) // tiles_wide
        pixel_x_in_tile = i & 0x3
        pixel_y_in_tile = (i & 0x1f) >> 2
        pixel_pair_index = (64 * tiles_wide * tile_y) + (8 * tiles_wide * pixel_y_in_tile) + \
                           (8 * tile_x) + pixel_x_in_tile * 2

        img_data[pixel_pair_index] = pixel_1
        img_data[pixel_pair_index + 1] = pixel_2

    img = Image.new('P', (tiles_wide * 8, tiles_high * 8))
    img.putdata(img_data)
    img.putpalette(GRAY_SCALE_PALETTE)
    return img

