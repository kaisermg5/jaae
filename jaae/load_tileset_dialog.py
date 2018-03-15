
from PyQt5 import QtWidgets, QtGui

from .jaae_handler import JaaeError
from . import main_window
from .load_tileset_ui import Ui_LoadTilesetDialog


class LoadTilesetDialog(QtWidgets.QDialog):
    def __init__(self, handler):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_LoadTilesetDialog()
        self.ui.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(main_window.ICON_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.handler = handler

        self.ui.amap_tileset_number_txt.textChanged.connect(self.amap_tileset_number_changed)
        self.ui.amap_tileset_number_txt.returnPressed.connect(self.translate_from_amap_number)
        self.ui.translate_btn.clicked.connect(self.translate_from_amap_number)
        self.ui.translate_btn.setEnabled(False)
        self.ui.tileset_header_txt.textChanged.connect(self.tileset_header_offset_changed)
        self.ui.tileset_header_txt.returnPressed.connect(self.load_tileset)
        self.ui.load_tileset_btn.clicked.connect(self.load_tileset)
        self.ui.load_tileset_btn.setEnabled(False)


    def error_message(self, description):
        QtWidgets.QMessageBox.critical(self, 'Error', description)

    def load_tileset(self):
        txt = self.ui.tileset_header_txt.text()
        if txt:
            try:
                offset = int(txt, base=0)
            except ValueError:
                self.error_message('Invalid number.')
                return
            try:
                self.handler.load_tileset(offset)
                self.accept()
            except JaaeError as e:
                self.error_message(str(e))

    def translate_from_amap_number(self):
        txt = self.ui.amap_tileset_number_txt.text()
        if txt:
            try:
                tileset_number = int(txt, base=0)
            except ValueError:
                self.error_message('Invalid number.')
                return
            try:
                self.ui.tileset_header_txt.setText(
                    hex(self.handler.get_header_offset_from_amap_tileset_number(tileset_number))
                )
            except JaaeError as e:
                self.error_message(str(e))

    def amap_tileset_number_changed(self):
        self.ui.translate_btn.setEnabled(
            self.ui.amap_tileset_number_txt.text().strip() != ''
        )

    def tileset_header_offset_changed(self):
        self.ui.load_tileset_btn.setEnabled(
            self.ui.tileset_header_txt.text().strip() != ''
        )


