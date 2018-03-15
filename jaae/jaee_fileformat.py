
from .animation import Animation


class InvalidJaaeFileFormat(Exception):
    pass

HEADER_SIZE = 4 + 1 + 1 + 2 + 2


def serialize_frames(frames_dict):
    max_length = -1
    for label in frames_dict:
        if not isinstance(label, str):
            raise InvalidJaaeFileFormat('All labels must be strings.')
        elif ' ' in label:
            raise InvalidJaaeFileFormat("Labels can't contain spaces.")
        max_length = max(len(label), max_length)

    label_data = b''
    img_data = b''
    for label in frames_dict:
        curr_label_data = (label + ' ' * (max_length - len(label))).encode('utf-8')
        if len(curr_label_data) > max_length:
            raise InvalidJaaeFileFormat('The label contains invalid characters.')

        label_data += curr_label_data + len(frames_dict[label]).to_bytes(4, 'little')
        img_data += frames_dict[label]

    return label_data + img_data, max_length


def serialize_animations(animations, label_length, label_list):
    data = b''
    for animation in animations:
        data += animation.start_tile.to_bytes(2, 'little')
        data += animation.end_tile.to_bytes(2, 'little')
        data += animation.speed.to_bytes(1, 'little')
        data += (len(animation.frames) - 1).to_bytes(2, 'little')
        for label in animation.frames:
            if label is None:
                label = ''
            elif label not in label_list:
                raise InvalidJaaeFileFormat('Label not found.')
            data += (label + ' ' * (label_length - len(label))).encode('utf-8')
    return data


def save_file(filename, animations, frames_dict):
    if len(animations) == 0:
        raise InvalidJaaeFileFormat('No animations given.')
    elif len(frames_dict) == 0:
        raise InvalidJaaeFileFormat('No frames given.')

    frames_data, label_length = serialize_frames(frames_dict)
    animations_data = serialize_animations(animations, label_length, frames_dict.keys())

    header_version = b'\x00'
    animations_count = (len(animations) - 1).to_bytes(1, 'little')
    frames_count = (len(frames_dict) - 1).to_bytes(2, 'little')
    header_data = B'JAAE' + header_version + animations_count + frames_count + \
                  label_length.to_bytes(2, 'little')

    with open(filename, 'wb') as f:
        f.write(header_data)
        f.write(frames_data)
        f.write(animations_data)


def deserialize_frames(data, frames_count, label_length, offset):
    data_offset = offset + frames_count * (label_length + 4)
    frames_dict = {}
    for i in range(frames_count):
        label = data[offset:offset + label_length].decode('utf-8').strip()
        data_size = int.from_bytes(data[offset + label_length:offset + label_length + 4], 'little')
        frames_dict[label] = data[data_offset:data_offset + data_size]
        offset += label_length + 4
        data_offset += data_size

    return frames_dict, data_offset  # data_offset has the start of the animations' data


def deserialize_animations(data, animations_count, offset, label_length, labels_list):
    animations = []
    for i in range(animations_count):
        start_tile = int.from_bytes(data[offset:offset + 2], 'little')
        end_tile = int.from_bytes(data[offset + 2:offset + 4], 'little')
        speed = data[offset + 4]
        frame_count = int.from_bytes(data[offset + 5:offset + 7], 'little') + 1

        animation = Animation(start_tile, end_tile, frame_count, speed)
        offset += 7
        for j in range(frame_count):
            label = data[offset:offset + label_length].decode('utf-8').strip()
            if label == '':
                animation.frames[j] = None
            elif label not in labels_list:
                raise InvalidJaaeFileFormat('Unknown label.')
            else:
                animation.frames[j] = label
            offset += label_length
        animations.append(animation)
    return animations


def read_file(filename):
    with open(filename, 'rb') as f:
        contents = f.read()

    if contents[0:4] != b'JAAE':
        raise InvalidJaaeFileFormat('Not a JAAE file.')
    elif contents[4] != 0:
        raise InvalidJaaeFileFormat('Unknown JAAE file format version.')

    animations_count = contents[5] + 1
    frames_count = int.from_bytes(contents[6:8], 'little') + 1
    label_length = int.from_bytes(contents[8:10], 'little')

    frame_dict, animations_data_offset = deserialize_frames(
        contents, frames_count, label_length, HEADER_SIZE
    )

    animations = deserialize_animations(
        contents, animations_count, animations_data_offset, label_length, frame_dict.keys()
    )

    return animations, frame_dict




