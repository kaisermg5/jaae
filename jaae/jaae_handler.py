
import os
import sys
import math
import re
import shutil
import subprocess


from PIL import Image

from . import lz77
from . import gba_image
from .animation import Animation
from . import jaae_fileformat


class JaaeError(Exception):
    pass


JAAE_BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))


def read_pointer(data):
    return int.from_bytes(data, 'little') & 0x7ffffff


class JaaeHandler:
    MAIN_TILESETS_HEADER_OFFSETS = {
        'BPEE': 0x3df704,
        'BPRE': 0x2d4a94,
        'AXVE': 0x286cf4
    }

    ROUTINE_SIZE = 0x84
    AS = 'arm-none-eabi-as'
    TMP_SRC = os.path.join(JAAE_BASE_PATH, 'tmp_animation_table.inc')
    TMP_OBJECT = os.path.join(JAAE_BASE_PATH, 'tmp.o')
    TMP_BIN = os.path.join(JAAE_BASE_PATH, 'base_routines.bin')
    OBJCOPY = 'arm-none-eabi-objcopy'
    AS_OPTIONS = ('-mthumb', 'resources/base_routines.s', '-o', TMP_OBJECT)
    OBJCOPY_OPTIONS = ('-O', 'binary', TMP_OBJECT, TMP_BIN)

    def __init__(self, user_interface_obj=None):
        self.user_interface_obj = user_interface_obj
        self.rom_filename = None
        self.rom_code = None
        self.tileset_header_offset = None
        self.is_primary_tileset = None
        self.tileset_palettes = [None] * 16
        self.tileset_img = None
        self.selected_palette = 0
        self.working_animation = None
        self.animations = []
        self.working_frame = None
        self.frames = {}

    def get_filedialog_path(self):
        return '.'

    def set_rom_filename(self, filename):
        if self.rom_filename is not None:
            self.rom_code = None
            self.tileset_header_offset = None
            self.is_primary_tileset = None
            self.tileset_palettes = [None] * 16
            self.tileset_img = None
        self.rom_filename = filename

    def rom_loaded(self):
        return self.rom_filename is not None

    def tileset_loaded(self):
        return self.tileset_img is not None

    def read_rom_code(self, contents=None):
        if contents is None:
            with open(self.rom_filename, 'rb') as f:
                f.seek(0xac)
                rom_code = (f.read(4)).decode('utf-8')
        else:
            rom_code = contents[0xac:0xb0].decode('utf-8')
        if rom_code not in ('BPEE', 'BPRE', 'AXVE'):
            raise JaaeError('Unknown rom code "{0}".'.format(rom_code))
        self.rom_code = rom_code

    def get_header_offset_from_amap_tileset_number(self, tileset_number):
        if self.rom_code is None:
            self.read_rom_code()
        return self.MAIN_TILESETS_HEADER_OFFSETS[self.rom_code] + (tileset_number * 24)

    def load_tileset(self, offset):
        offset &= 0x7ffffff
        with open(self.rom_filename, 'rb') as f:
            contents = f.read()
        if self.rom_code is None:
            self.read_rom_code(contents)

        if len(contents) < (offset + 8):
            raise JaaeError('The header offset "{0}" is too big.'.format(hex(offset)))

        tileset_img_offset = read_pointer(contents[offset + 4:offset + 8])
        if len(contents) <= tileset_img_offset:
            raise JaaeError('The image offset "{0}" is too big.'.format(hex(tileset_img_offset)))
        if contents[offset]:  # tileset is compressed
            try:
                tileset_data, _ = lz77.decompress(contents[tileset_img_offset::])
            except lz77.InvalidLz77Data:
                raise JaaeError('Tileset header point to invalid image data.')
        else:
            tileset_data = contents[tileset_img_offset:tileset_img_offset + 32 * 512]

        self.tileset_img = gba_image.from_4bpp_to_img(tileset_data, 16)
        self.is_primary_tileset = contents[offset + 1] == 0

        tileset_palettes_offset = read_pointer(contents[offset + 8:offset + 12])
        if len(contents) < (tileset_palettes_offset + 16 * 32):
            raise JaaeError('The palettes offset "{0}" is too big.'.format(
                hex(tileset_palettes_offset))
            )
        for i in range(16):
            self.tileset_palettes[i] = gba_image.from_gba_to_pal(
                contents[tileset_palettes_offset:tileset_palettes_offset + 32]
            )
            tileset_palettes_offset += 32
        self.selected_palette = 0
        self.tileset_header_offset = offset

    def get_tileset_image(self, copy=False):
        if copy:
            img = self.tileset_img.copy()
        else:
            img = self.tileset_img
        img.putpalette(self.tileset_palettes[self.selected_palette])
        return img

    def set_selected_palette(self, index):
        if not (0 <= index < 16):
            raise JaaeError('Invalid palette index')
        self.selected_palette = index

    def get_selected_palette(self):
        return self.selected_palette

    def get_tileset_header_offset(self):
        return self.tileset_header_offset

    def can_add_animation(self):
        return len(self.animations) < 20

    def get_animations_count(self):
        return len(self.animations)

    def add_animation(self):
        if not self.can_add_animation():
            raise JaaeError('Cannot add more than 20 animations.')
        self.animations.append(Animation())
        if self.working_animation is None:
            self.working_animation = 0
        if self.working_frame is None or \
                not 0 <= self.working_frame < self.get_animation_frame_count():
            self.working_frame = 0

    def set_working_animation(self, index):
        if not 0 <= index < len(self.animations):
            raise JaaeError('Invalid index.')
        self.working_animation = index
        if self.working_frame >= self.get_animation_frame_count():
            self.working_frame = self.get_animation_frame_count() - 1

    def remove_working_animation(self):
        del self.animations[self.working_animation]
        if len(self.animations) == 0:
            self.working_animation = None
            self.working_frame = None
        else:
            self.working_animation = min((self.working_animation, len(self.animations) - 1))
            self.working_frame = 0

    def get_working_animation(self):
        return self.working_animation

    def get_animation_start(self):
        return self.animations[self.working_animation].start_tile

    def set_animation_start(self, value):
        if len(self.animations) > 0:
            if not 0 <= value <= 0xffff:
                raise JaaeError('Invalid value')
            self.animations[self.working_animation].start_tile = value
            if value > self.animations[self.working_animation].end_tile:
                self.animations[self.working_animation].end_tile = value

    def get_animation_end(self):
        return self.animations[self.working_animation].end_tile

    def set_animation_end(self, value):
        if len(self.animations) > 0:
            if not 0 <= value <= 0xffff:
                raise JaaeError('Invalid value')
            self.animations[self.working_animation].end_tile = value
            if value < self.animations[self.working_animation].start_tile:
                self.animations[self.working_animation].start_tile = value

    def get_animation_speed(self):
        return self.animations[self.working_animation].speed

    def set_animation_speed(self, value):
        if not 0 <= value < 8:
            raise JaaeError('Invalid speed.')
        self.animations[self.working_animation].speed = value

    def get_animation_frame_index(self):
        return math.log(self.get_animation_frame_count(), 2) - 1

    def get_animation_frame_count(self):
        if self.working_animation is None:
            return 0
        return self.animations[self.working_animation].get_frame_count()

    def set_animation_frame_count(self, index):
        value = 1 << (index + 1)
        if value > 32:
            raise JaaeError('The index is too big')
        if not self.animations[self.working_animation].can_safely_trim(value) and \
                not self.user_interface_obj.yes_no_question(
                    'Change number of frames',
                    ('There are frames over {0} that are being used.\n'
                     '¿Do you wish to delete them anyways?').format(value)
                ):
            return False

        self.animations[self.working_animation].set_frame_count(value)
        if not self.working_frame < index:
            self.working_frame = index - 1
        return True

    def get_working_frame(self):
        return self.working_frame

    def set_selected_frame(self, index):
        if not 0 <= index < self.get_animation_frame_count():
            raise JaaeError('Invalid index.')
        self.working_frame = index

    def add_frame(self, label, img_path, split_image_in=1):
        if re.match(r'^[a-zA-Z0-9_]+$', label) is None:
            raise JaaeError('Labels can only have letters, numbers and underscores.')
        elif split_image_in < 1:
            raise JaaeError('Invalid divisor.')

        if split_image_in == 1:
            labels_to_add = (label,)
        else:
            labels_to_add = ['{0}_{1}'.format(label, i) for i in range(split_image_in)]

        for label_to_add in labels_to_add:
            for label2 in self.frames:
                if label_to_add == label2:
                    raise JaaeError('Label "{0}" already used.'.format(label))

        # Get image data
        try:            
            img = Image.open(img_path)
        except OSError:
            raise JaaeError('Not a valid image.')
        try:
            data = gba_image.from_img_to_4bpp(img)
        except gba_image.ImageFormatError as e:
            raise JaaeError(str(e))

        if len(data) % (32 * split_image_in) != 0:
            raise JaaeError('Cannot split image in "{0}" frames.'.format(split_image_in))

        frame_size = len(data) // split_image_in
        for i in range(len(labels_to_add)):
            self.frames[labels_to_add[i]] = data[i * frame_size:(i + 1) * frame_size]

    def animation_matches_frame(self):
        if self.working_animation is None or self.working_frame is None:
            return True
        label = self.animations[self.working_animation].frames[self.working_frame]
        if label is None:
            return True
        start = self.get_animation_start()
        end = self.get_animation_end()
        return (end - start + 1) == (len(self.frames[label]) // 32)

    def is_frame_used(self, label, exclude_working_frame=True):
        for i in range(len(self.animations)):
            for j in range(len(self.animations[i].frames)):
                if exclude_working_frame and i == self.working_animation and \
                                j == self.working_frame:
                    continue

                if self.animations[i].frames[j] == label:
                    return True
        return False

    def remove_frame(self, label):
        if self.is_frame_used(label):
            if self.user_interface_obj.yes_no_question(
                'Remove frame',
                'The selected frame is being used for some animations.\n¿Remove anyways?'
            ):
                for i in range(len(self.animations)):
                    for j in range(len(self.animations[i].frames)):
                        if self.animations[i].frames[j] == label:
                            self.animations[i].frames[j] = None
            else:
                return False
        else:
            self.animations[self.working_animation].frames[self.working_frame] = None
        del self.frames[label]
        return True

    def get_all_frames_count(self):
        return len(self.frames)

    def get_frame_labels(self):
        return self.frames.keys()

    def set_working_frame_image(self, label):
        if label not in self.frames:
            raise JaaeError('Invalid label.')
        self.animations[self.working_animation].frames[self.working_frame] = label

    def get_working_frame_image_label(self):
        if self.working_animation is None or self.working_frame is None:
            return None
        return self.animations[self.working_animation].frames[self.working_frame]

    def get_working_frame_image(self, tiles_wide):
        label = self.get_working_frame_image_label()
        if label is None:
            return None
        data = self.frames[label]
        if data is None:
            return None
        img = gba_image.from_4bpp_to_img(
            data,
            tiles_wide
        )
        img.putpalette(self.tileset_palettes[self.selected_palette])
        return img

    def export_animations(self, filename):
        if len(self.animations) == 0 and len(self.frames) == 0:
            raise JaaeError('There has to be at least one animation and one frame to save.')
        jaae_fileformat.save_file(filename, self.animations, self.frames)

    def import_animations(self, filename):
        if self.tileset_img is None:
            raise JaaeError('No tileset loaded.')
        try:
            self.animations, self.frames = jaae_fileformat.read_file(filename)
            self.working_animation = 0
            self.working_frame = 0
        except jaae_fileformat.InvalidJaaeFileFormat:
            raise JaaeError('Invalid JAAE file.')

    def get_needed_space(self):
        size = self.ROUTINE_SIZE + len(self.animations) * 8
        for animation in self.animations:
            size += 4 * len(animation.frames)
        for label in self.frames:
            size += len(self.frames[label])
        return size

    def insert_to_rom(self, offset):
        if not 0 <= offset < 0x10000000:
            raise JaaeError('Invalid offset')
        if offset % 4 != 0:
            raise JaaeError('The offset must be aligned. It has to end in 0, 4, 8 or C.')
        offset &= 0x7ffffff

        # Check environment
        initial_path = os.path.abspath('.')
        if initial_path != JAAE_BASE_PATH:
            os.chdir(JAAE_BASE_PATH)

        if shutil.which(self.AS) is None or shutil.which(self.OBJCOPY) is None:
            if 'DEVKITARM' in os.environ:
                os.environ['PATH'] = os.path.join(os.environ['DEVKITARM'], 'bin') + \
                                     os.pathsep + os.environ['PATH']
                if shutil.which(self.AS) is None or shutil.which(self.OBJCOPY) is None:
                    raise JaaeError("DevkitARM isn't set up correctly.")
            else:
                raise JaaeError("DEVKITARM environment variable isn't set.")

        # Generate frames text
        frames_txt = ''
        for label in self.frames:
            frames_txt += 'frame_img_{0}:\n.byte {1}\n'.format(
                label, ','.join(str(n) for n in self.frames[label])
            )
        # Generate animation table text
        animation_header_table_txt = '.align 2\nAnimHeaderTable:\n'
        frames_tables_txt = ''
        for i in range(len(self.animations)):
            animation_header_table_txt += 'anim_table_entry {0} + INSERTION_OFFSET, {1}, {2}, {3}, {4}\n'.format(
                'AnimationTable{0}'.format(i),
                self.animations[i].start_tile,
                self.animations[i].end_tile - self.animations[i].start_tile + 1,
                self.animations[i].speed,
                self.get_animation_frame_count() - 1
            )

            frames_tables_txt += 'AnimationTable{0}:\n'.format(i)
            for j in range(len(self.animations[i].frames)):
                if self.animations[i].frames[j] is None:
                    raise JaaeError('In animation {0}, frame {1} has no assigned image.'.format(i, j))
                frames_tables_txt += '.4byte frame_img_{0} + INSERTION_OFFSET\n'.format(
                    self.animations[i].frames[j]
                )
        animation_header_table_txt += 'AnimHeaderTableEnd:\n'

        # Save temp text file
        with open(self.TMP_SRC, 'w') as f:
            f.write(animation_header_table_txt)
            f.write(frames_tables_txt)
            f.write(frames_txt)

        # Assemble
        inserted = False
        output_txt = ''
        p = subprocess.Popen(
            args=[
                self.AS, '--defsym', '{0}=1'.format(self.rom_code), '--defsym',
                'INSERTION_OFFSET={0}'.format(0x8000000 | offset), '--defsym',
                '{0}=1'.format(('SECONDARY', 'PRIMARY')[self.is_primary_tileset]),
                *self.AS_OPTIONS
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, _ = p.communicate()
        output_txt += stdout.decode('utf-8', errors='ignore')
        if p.returncode == 0:
            output_txt += '\nAssembled successfully.\n'

            # Generate binary
            p = subprocess.Popen(
                args=[self.OBJCOPY, *self.OBJCOPY_OPTIONS],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = p.communicate()
            output_txt += stdout.decode('utf-8', errors='ignore')

            if p.returncode == 0:
                output_txt += '\nBinary generated successfully.\n'

                # Insert to rom
                with open(self.rom_filename, 'rb+') as f:
                    # Write pointer to the routine
                    f.seek(self.tileset_header_offset + (0x14, 0x10)[self.rom_code == 'BPRE'])
                    f.write((offset | 0x8000001).to_bytes(4, 'little'))

                    # Write routine
                    f.seek(offset)
                    if f.tell() != offset:
                        f.write(b'\xff' * (offset - f.tell()))
                    with open(self.TMP_BIN, 'rb') as f2:
                        f.write(f2.read())
                    inserted = True

            else:
                output_txt += '\nError generating binary.\n'
        else:
            output_txt += '\nAssembling failed.\n'

        # Delete tmp files
        if os.path.exists(self.TMP_BIN):
            os.remove(self.TMP_BIN)
        if os.path.exists(self.TMP_OBJECT):
            os.remove(self.TMP_OBJECT)
        if os.path.exists(self.TMP_SRC):
            os.remove(self.TMP_SRC)

        if initial_path != JAAE_BASE_PATH:
            os.chdir(initial_path)

        return output_txt, inserted

