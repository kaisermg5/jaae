
import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from .main_window_ui import Ui_mainWindow
from .jaae_handler import JaaeHandler, JaaeError, JAAE_BASE_PATH
from .load_tileset_dialog import LoadTilesetDialog
from .insert_to_rom_dialog import InsertToRomDialog
from .tilemap_scene import TilemapScene


ICON_PATH = os.path.abspath(os.path.join(JAAE_BASE_PATH, 'resources/jaae.ico'))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(ICON_PATH), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.handler = JaaeHandler(self)

        # Connect menu bar
        self.ui.actionLoad_ROM.triggered.connect(self.load_rom)
        self.ui.actionInsert_to_ROM.triggered.connect(self.insert_to_rom)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionLoad_Tileset.triggered.connect(self.load_tileset)
        self.ui.actionImport_Animations.triggered.connect(self.import_animations)
        self.ui.actionExport_Animations.triggered.connect(self.export_animations)

        # Tileset groupbox
        self.tileset_scene = TilemapScene(16, clicked_event=self.tileset_clicked)
        self.ui.tileset_view.setScene(self.tileset_scene)
        self.ui.palette_cmb.currentIndexChanged.connect(self.selected_palette_changed)
        self.header_offset_font = QtGui.QFont(self.ui.header_offset_txt.font())
        self.ui.header_offset_txt.textEdited.connect(self.header_offset_changed)
        self.ui.add_animation_btn.clicked.connect(self.add_animation)

        # Animation groupbox
        self.ui.animation_number_cmb.currentIndexChanged.connect(self.working_animation_changed)
        self.ui.frame_number_cmb.currentIndexChanged.connect(self.working_frame_changed)
        self.ui.frame_quantity_cmb.currentIndexChanged.connect(self.frame_count_changed)
        self.ui.frame_speed_cmb.currentIndexChanged.connect(self.speed_changed)
        self.ui.start_tile_txt.textEdited.connect(self.start_tile_changed)
        self.ui.start_tile_txt.returnPressed.connect(self.start_tile_return_pressed)
        self.start_tile_font = QtGui.QFont(self.ui.start_tile_txt.font())
        self.ui.end_tile_txt.textEdited.connect(self.end_tile_changed)
        self.ui.end_tile_txt.returnPressed.connect(self.end_tile_return_pressed)
        self.end_tile_font = QtGui.QFont(self.ui.end_tile_txt.font())
        self.ui.remove_animation_btn.clicked.connect(self.remove_animation)

        # Frame groupbox
        self.ui.preview_wide_spb.valueChanged.connect(self.frame_preview_wide_changed)
        self.frame_preview_scene = TilemapScene(16)
        self.ui.frame_preview.setScene(self.frame_preview_scene)
        self.ui.add_frame_btn.clicked.connect(self.add_frame)
        self.ui.frame_lst.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.ui.frame_lst.itemSelectionChanged.connect(self.select_frame_from_list)
        self.ui.frame_warnings_lbl.setVisible(False)
        self.ui.frame_warnings_lbl.setStyleSheet('QLabel { color: red }')
        self.ui.remove_frame_btn.clicked.connect(self.remove_frame)

        self.ui.tileset_grb.setEnabled(False)
        self.ui.menuEdit.setEnabled(False)
        self.ui.actionInsert_to_ROM.setEnabled(False)

    @staticmethod
    def call_disabling_signals(obj, funct_to_call):
        obj.blockSignals(True)
        funct_to_call()
        obj.blockSignals(False)

    @classmethod
    def silently_set_combobox_current_index(cls, cmb, index):
        cls.call_disabling_signals(
            cmb,
            lambda: cmb.setCurrentIndex(index)
        )

    @staticmethod
    def yes_no_question(title, question, informative_text=None):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        msgbox.setText(question)
        msgbox.setIcon(QtWidgets.QMessageBox.Question)
        if informative_text is not None:
            msgbox.setInformativeText(informative_text)
        msgbox.setStandardButtons(
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        msgbox.setDefaultButton(QtWidgets.QMessageBox.No)
        return msgbox.exec() == QtWidgets.QMessageBox.Yes

    # Dialogs:
    def open_file_dialog(self, title, file_type='All files (*)'):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, title,
            self.handler.get_filedialog_path(),
            file_type
        )
        return filename

    def error_message(self, title, description):
        QtWidgets.QMessageBox.critical(self, title, description)

    def closeEvent(self, event):
        if not self.handler.get_animations_count() or self.yes_no_question('There are animations loaded', "Are you sure you wan't to exit?"):
            event.accept()
        else:
            event.ignore()

    def load_rom(self):
        filename = self.open_file_dialog('Open ROM', 'GBA rom (*.gba)')
        if filename:
            if self.handler.rom_loaded():
                self.ui.tileset_grb.setEnabled(False)
                self.ui.header_offset_txt.setText('')
                self.tileset_scene.clear()
            self.handler.set_rom_filename(filename)
            self.ui.menuEdit.setEnabled(True)
            self.ui.actionInsert_to_ROM.setEnabled(True)

    def insert_to_rom(self):
        if self.handler.get_animations_count() > 0:
            InsertToRomDialog(self.handler).exec()
        else:
            self.error_message('Error', 'No animations to insert.')

    def load_tileset(self):
        if LoadTilesetDialog(self.handler).exec() == QtWidgets.QDialog.Accepted:
            self.silently_set_combobox_current_index(
                self.ui.palette_cmb,
                self.handler.get_selected_palette()
            )
            self.ui.header_offset_txt.setText(hex(self.handler.get_tileset_header_offset()))

            self.update_animations()
            self.update_tileset_preview()
            self.ui.tileset_grb.setEnabled(True)

    def import_animations(self):
        if self.handler.tileset_loaded():
            filename = self.open_file_dialog('Import Animations', 'JAAE file (*.jaae) ;; All Files (*)')
            if filename:
                try:
                    self.handler.import_animations(filename)
                except JaaeError as e:
                    self.error_message('Error', str(e))
                    return
                self.update_animations()
                self.update_tileset_preview()
                self.update_frames()
        else:
            self.error_message('Error', 'No tileset loaded.')

    def export_animations(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Export Animations',
            self.handler.get_filedialog_path(),
            'JAAE file (*.jaae)'
        )
        if filename:
            if not filename.endswith('.jaae'):
                filename += '.jaae'
            try:
                self.handler.export_animations(filename)
            except JaaeError as e:
                self.error_message('Error', str(e))

    def update_tileset_preview(self):
        img = self.handler.get_tileset_image()
        w, h = img.size
        img = img.resize((w * 2, h * 2))
        self.tileset_scene.set_image(img)

        if self.handler.get_animations_count() > 0:
            start = self.handler.get_animation_start()
            end = self.handler.get_animation_end()
            self.tileset_scene.draw_rectangle_over_tiles(
                start, end, color=QtGui.QColor(255, 255, 255, 100), fill=True
            )

    def update_animations_start_and_end(self):
        self.start_tile_font.setBold(False)
        self.ui.start_tile_txt.setText(hex(self.handler.get_animation_start()))
        self.ui.start_tile_txt.setFont(self.start_tile_font)
        self.end_tile_font.setBold(False)
        self.ui.end_tile_txt.setText(hex(self.handler.get_animation_end()))
        self.ui.end_tile_txt.setFont(self.end_tile_font)

    def update_animations(self, update_working_animation_combobox=True):
        self.ui.add_animation_btn.setEnabled(self.handler.can_add_animation())
        animations_quantity = self.handler.get_animations_count()
        if animations_quantity > 0:
            self.ui.animations_grb.setEnabled(True)
            if update_working_animation_combobox and \
                    animations_quantity != self.ui.animation_number_cmb.count():
                self.ui.animation_number_cmb.blockSignals(True)
                self.ui.animation_number_cmb.clear()
                self.ui.animation_number_cmb.addItems(str(i) for i in range(animations_quantity))
                self.ui.animation_number_cmb.blockSignals(False)

            self.update_animations_start_and_end()

            self.silently_set_combobox_current_index(
                self.ui.frame_speed_cmb,
                self.handler.get_animation_speed()
            )
            self.silently_set_combobox_current_index(
                self.ui.frame_quantity_cmb,
                self.handler.get_animation_frame_index()
            )
        else:
            self.ui.animations_grb.setEnabled(False)
            self.ui.start_tile_txt.clear()
            self.ui.end_tile_txt.clear()

    def update_frame_preview(self):
        frame_img = self.handler.get_working_frame_image(self.ui.preview_wide_spb.value())
        if frame_img is not None:
            w, h = frame_img.size
            frame_img = frame_img.resize((w * 2, h * 2))
            self.frame_preview_scene.set_image(frame_img)
        else:
            self.frame_preview_scene.clear()

    def update_frame_list_selection(self):
        selected_label = self.handler.get_working_frame_image_label()
        if selected_label is not None:
            index = None
            for i in range(self.ui.frame_lst.count()):
                if self.ui.frame_lst.item(i).text() == selected_label:
                    index = i
                    break
            if index is not None:
                self.ui.frame_lst.setCurrentRow(index)
            else:
                raise Exception("The list doens't contain all items")
        else:
            self.ui.frame_lst.clearSelection()

    def update_frame_list_items(self, force_update_selection=False):
        if self.ui.frame_lst.count() != self.handler.get_all_frames_count():
            self.ui.frame_lst.clear()
            self.ui.frame_lst.addItems(self.handler.get_frame_labels())
            self.update_frame_list_selection()
        elif force_update_selection:
            self.update_frame_list_selection()

    def update_frames_combobox(self):
        frame_count = self.handler.get_animation_frame_count()
        if self.ui.frame_number_cmb.count() != frame_count:
            curr_index = self.ui.frame_number_cmb.currentIndex()
            self.ui.frame_number_cmb.blockSignals(True)
            self.ui.frame_number_cmb.clear()
            self.ui.frame_number_cmb.addItems(str(i) for i in range(frame_count))
            if 0 <= curr_index < frame_count:
                self.ui.frame_number_cmb.setCurrentIndex(curr_index)
            self.ui.frame_number_cmb.blockSignals(False)

    def update_frame_warning(self):
        self.ui.frame_warnings_lbl.setVisible(not self.handler.animation_matches_frame())

    def update_frames(self):
        self.update_frame_list_items(force_update_selection=True)
        self.update_frames_combobox()
        self.update_frame_preview()
        self.update_frame_warning()

    def selected_palette_changed(self):
        self.handler.set_selected_palette(self.ui.palette_cmb.currentIndex())
        self.update_tileset_preview()
        self.update_frame_preview()

    def header_offset_changed(self):
        self.header_offset_font.setBold(True)
        self.ui.header_offset_txt.setFont(self.header_offset_font)

    def add_animation(self):
        previous_working_animation = self.handler.get_working_animation()
        self.handler.add_animation()
        self.update_animations()
        if previous_working_animation != self.handler.get_working_animation():
            self.update_tileset_preview()
            self.update_frames()

    def tileset_clicked(self, event):
        if self.handler.get_animations_count() > 0:
            button = event.button()
            tile_num = self.tileset_scene.get_clicked_tile(event)
            if button == QtCore.Qt.LeftButton:
                self.handler.set_animation_start(tile_num)
            elif button == QtCore.Qt.RightButton:
                self.handler.set_animation_end(tile_num)
            self.update_tileset_preview()
            self.update_animations()
            self.update_frame_warning()

    def remove_animation(self):
        if self.yes_no_question(
                'Remove Animation',
                '¿Are you sure you want to remove this animation?'
        ):
            self.handler.remove_working_animation()
            self.update_animations()
            self.update_tileset_preview()
            self.update_frames()

    def working_animation_changed(self):
        self.handler.set_working_animation(self.ui.animation_number_cmb.currentIndex())

        self.update_animations(update_working_animation_combobox=False)
        self.update_tileset_preview()
        self.update_frames()

    def start_tile_changed(self):
        self.start_tile_font.setBold(True)
        self.ui.start_tile_txt.setFont(self.start_tile_font)

    def start_tile_return_pressed(self):
        try:
            value = int(self.ui.start_tile_txt.text(), base=0)
            self.handler.set_animation_start(value)
        except (ValueError, JaaeError) as e:
            msg = (str(e), 'Invalid number.')[isinstance(e, ValueError)]
            self.error_message('Error', msg)
            self.ui.start_tile_txt.setText(hex(self.handler.get_animation_start()))

        self.update_animations_start_and_end()
        self.update_tileset_preview()

    def end_tile_changed(self):
        self.end_tile_font.setBold(True)
        self.ui.end_tile_txt.setFont(self.end_tile_font)

    def end_tile_return_pressed(self):
        try:
            value = int(self.ui.end_tile_txt.text(), base=0)
            self.handler.set_animation_end(value)
        except (ValueError, JaaeError) as e:
            msg = (str(e), 'Invalid number.')[isinstance(e, ValueError)]
            self.error_message('Error', msg)
            self.ui.end_tile_txt.setText(hex(self.handler.get_animation_end()))

        self.update_animations_start_and_end()
        self.update_tileset_preview()

    def frame_count_changed(self):
        working_frame = self.handler.get_working_frame()
        if self.handler.set_animation_frame_count(self.ui.frame_quantity_cmb.currentIndex()):
            if working_frame == self.handler.get_working_frame():
                self.update_frames_combobox()
            else:
                self.update_frames()
        else:
            self.silently_set_combobox_current_index(
                self.ui.frame_quantity_cmb,
                self.handler.get_animation_frame_index()
            )

    def speed_changed(self):
        self.handler.set_animation_speed(self.ui.frame_speed_cmb.currentIndex())

    def frame_preview_wide_changed(self):
        self.update_frame_preview()

    def add_frame(self):
        label = self.ui.add_frame_label_txt.text().strip()
        if label:
            frame_filename = self.open_file_dialog('Open Image', 'PNG (*.png); All (*)')

            if frame_filename:
                try:
                    self.handler.add_frame(
                        label,
                        frame_filename,
                        self.ui.split_image_in_spb.value()
                    )
                    self.update_frame_list_items()
                except JaaeError as e:
                    self.error_message('Error', str(e))
        else:
            self.error_message('Error', 'No label given.')

    def remove_frame(self):
        selected_items = self.ui.frame_lst.selectedItems()
        if len(selected_items) > 0 and self.handler.remove_frame(selected_items[0].text()):
            self.update_frames()

    def working_frame_changed(self):
        self.handler.set_selected_frame(self.ui.frame_number_cmb.currentIndex())
        self.update_frames()

    def select_frame_from_list(self):
        selected_items = self.ui.frame_lst.selectedItems()
        if len(selected_items) > 0:
            label = selected_items[0].text()
            if label != self.handler.get_working_frame_image_label():
                self.handler.set_working_frame_image(label)
                self.update_frame_list_selection()
                self.update_frame_preview()
                self.update_frame_warning()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    r = app.exec_()
    app.deleteLater()
    sys.exit(r)

if __name__ == '__main__':
    main()


