

SPEED_TOO_FAST = 0
SPEED_VERY_FAST = 1
SPEED_FAST = 2
SPEED_NORMAL = 3
SPEED_SLOW = 4
SPEED_VERY_SLOW = 5
SPEED_TOO_SLOW = 6
SPEED_IS_IT_EVEN_CHANGING = 7


class Animation:
    def __init__(self, start_tile=0, end_tile=0, frame_count=2, speed=SPEED_NORMAL):
        self.start_tile = start_tile
        self.end_tile = end_tile
        self.frames = [None] * frame_count
        self.speed = speed

    def get_frame_count(self):
        return len(self.frames)

    def set_frame_count(self, value):
        if value > len(self.frames):
            self.frames.extend(None for i in range(value - len(self.frames)))
        elif value < len(self.frames):
            del self.frames[value::]

    def can_safely_trim(self, new_frame_count):
        for i in range(new_frame_count, len(self.frames)):
            if self.frames[i] is not None:
                return False
        return True





