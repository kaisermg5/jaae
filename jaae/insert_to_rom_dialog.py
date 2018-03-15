
from PyQt5 import QtWidgets, QtGui

from .jaae_handler import JaaeError
from . import main_window
from .insert_to_rom_ui import Ui_InsertToRomDialog


class InsertToRomDialog(QtWidgets.QDialog):
    def __init__(self, handler):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_InsertToRomDialog()
        self.ui.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(main_window.ICON_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.handler = handler

        self.ui.free_space_txt.textChanged.connect(self.free_space_txt_changed)
        self.ui.free_space_txt.returnPressed.connect(self.insert_to_rom)
        self.ui.insert_btn.setEnabled(False)
        self.ui.insert_btn.clicked.connect(self.insert_to_rom)
        self.ui.needed_bytes_label.setText(str(self.handler.get_needed_space()))

    def error_message(self, description):
        QtWidgets.QMessageBox.critical(self, 'Error', description)

    def insert_to_rom(self):
        txt = self.ui.free_space_txt.text()
        if txt:
            try:
                offset = int(txt, base=0)
            except ValueError:
                self.error_message('Invalid number.')
                return

            if main_window.MainWindow.yes_no_question(
                'Inset to ROM',
                'Are you sure you want to insert the animations to the rom?'
            ):
                try:
                    output, result = self.handler.insert_to_rom(offset)
                except JaaeError as e:
                    self.error_message(str(e))
                    return
                self.ui.output_txt.setText(output)

                title, description = (
                    ('Insertion failed', 'Failed to insert the animations'),
                    ('Insertion sucessfull', 'Animations where inserted successfully')
                )[result]
                QtWidgets.QMessageBox.information(self, title, description, QtWidgets.QMessageBox.Ok)

    def free_space_txt_changed(self):
        self.ui.insert_btn.setEnabled(self.ui.free_space_txt.text() != '')

