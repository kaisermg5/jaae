
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageQt

from . import qmapview


class TilemapScene(QtWidgets.QGraphicsScene):
    def __init__(self, tile_size, img=None, clicked_event=None, clicked_dragged_event=None):
        super(TilemapScene, self).__init__()

        self.pixmap = None
        self.tiles_wide = None
        self.tile_size = tile_size
        self.clicked_event = clicked_event
        self.clicked_dragged_event = clicked_dragged_event

        if img is not None:
            self.set_image(img)

    def set_image(self, img):
        img_qt = ImageQt.ImageQt(img.convert('RGBA'))
        pixmap = QtGui.QPixmap.fromImage(img_qt)
        self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap):
        if self.pixmap is None or pixmap.width() != self.pixmap.pixmap.width():
            self.initialize_pixmap(pixmap)
        else:
            self.pixmap.set_pixmap(pixmap)
        self.tiles_wide = pixmap.width() // self.tile_size
        self.update()

    def initialize_pixmap(self, pixmap):
        self.clear()
        self.pixmap = qmapview.QMapPixmap(pixmap)
        self.addItem(self.pixmap)
        if self.clicked_event is not None:
            self.pixmap.clicked.connect(self.clicked_event)
        if self.clicked_dragged_event is not None:
            self.pixmap.click_dragged.connect(self.clicked_dragged_event)

    def get_clicked_tile(self, event):
        pos = event.pos()
        x = int(pos.x())
        y = int(pos.y())
        if x < 0 or y < 0 or x >= self.pixmap.pixmap.width() or y >= self.pixmap.pixmap.height():
            return -1

        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        tile_num = tile_x + tile_y * self.tiles_wide

        return tile_num

    def draw_square_over_tile(self, tile_num, color=QtCore.Qt.blue):
        x = (tile_num % self.tiles_wide) * self.tile_size
        y = (tile_num // self.tiles_wide) * self.tile_size

        drawer = QtGui.QPainter(self.pixmap.pixmap)
        drawer.setPen(color)
        drawer.drawRect(x, y, self.tile_size, self.tile_size)
        drawer.end()

    def draw_rectangle_over_tiles(self, start_tile, end_tile, color=QtCore.Qt.blue, fill=False):
        total_tiles_to_paint = end_tile - start_tile + 1
        start_tile_x = start_tile % self.tiles_wide
        y = (start_tile // self.tiles_wide) * self.tile_size
        drawer = QtGui.QPainter(self.pixmap.pixmap)
        drawer.setPen(color)
        if fill:
            drawer.setBrush(color)

        if start_tile_x != 0:
            x = start_tile_x * self.tile_size
            tiles_to_paint = self.tiles_wide - start_tile_x
            if total_tiles_to_paint < tiles_to_paint:
                tiles_to_paint = total_tiles_to_paint
            drawer.drawRect(x, y, self.tile_size * tiles_to_paint, self.tile_size)
            total_tiles_to_paint -= tiles_to_paint
            y += self.tile_size

        for i in range(total_tiles_to_paint // self.tiles_wide):
            drawer.drawRect(0, y, self.tile_size * self.tiles_wide, self.tile_size)
            y += self.tile_size
            total_tiles_to_paint -= self.tiles_wide

        if total_tiles_to_paint > 0:
            drawer.drawRect(0, y, self.tile_size * total_tiles_to_paint, self.tile_size)

        drawer.end()

    def clear(self):
        self.pixmap = None
        super(TilemapScene, self).clear()