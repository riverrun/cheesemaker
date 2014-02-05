# -*- coding: utf-8 -*-

# Authors: David Whitlock <alovedalongthe@gmail.com>
# A simple image viewer
# Copyright (C) 2013 David Whitlock
#
# Cheesemaker is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cheesemaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cheesemaker.  If not, see <http://www.gnu.org/licenses/gpl.html>.

from PyQt5 import QtCore, QtGui, QtWidgets, QtPrintSupport
from gi.repository import GExiv2
import os
import sys
import dbus
import random
from . import preferences, editimage

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent):
        QtWidgets.QMainWindow.__init__(self)

        self.printer = QtPrintSupport.QPrinter()
        self.create_actions()
        self.create_menu()
        self.create_dict()
        self.load_img = self.load_img_fit
        self.slides_next = True

        self.scene = QtWidgets.QGraphicsScene()
        self.img_view = ImageView(self)
        self.img_view.setScene(self.scene)
        self.setCentralWidget(self.img_view)

        self.read_prefs()
        self.readable_list = parent.readable_list
        self.writeable_list = ('bmp', 'jpg', 'jpeg', 'png', 'ppm', 'tif', 'tiff', 'xbm', 'xpm')
        self.resize(700, 500)

    def create_actions(self):
        self.open_act = QtWidgets.QAction('&Open', self, shortcut='Ctrl+O',
                triggered=self.open)
        self.reload_act = QtWidgets.QAction('&Reload image', self, shortcut='Ctrl+R',
                enabled=False, triggered=self.reload_img)
        self.print_act = QtWidgets.QAction('&Print', self, shortcut='Ctrl+P',
                enabled=False, triggered=self.print_img)
        self.save_act = QtWidgets.QAction('&Save image', self, shortcut='Ctrl+S',
                enabled=False, triggered=self.save_img)
        self.exit_act = QtWidgets.QAction('E&xit', self, shortcut='Ctrl+Q',
                triggered=self.close)
        self.fulls_act = QtWidgets.QAction('Fullscreen', self, shortcut='F11',
                enabled=False, checkable=True, triggered=self.toggle_fullscreen)
        self.ss_act = QtWidgets.QAction('Slideshow', self, shortcut='F5',
                enabled=False, checkable=True, triggered=self.toggle_slideshow)
        self.ss_next_act = QtWidgets.QAction('Next / Random image', self, enabled=False,
                checkable=True, triggered=self.set_slide_type)
        self.ss_next_act.setChecked(True)
        self.next_act = QtWidgets.QAction('Next image', self, shortcut='Right',
                enabled=False, triggered=self.go_next_img)
        self.prev_act = QtWidgets.QAction('Previous image', self, shortcut='Left',
                enabled=False, triggered=self.go_prev_img)
        self.rotleft_act = QtWidgets.QAction('Rotate left', self, shortcut='Ctrl+Left',
                enabled=False, triggered=self.img_rotate_left)
        self.rotright_act = QtWidgets.QAction('Rotate right', self, shortcut='Ctrl+Right',
                enabled=False, triggered=self.img_rotate_right)
        self.fliph_act = QtWidgets.QAction('Flip image horizontally', self, shortcut='Ctrl+H',
                enabled=False, triggered=self.img_fliph)
        self.flipv_act = QtWidgets.QAction('Flip image vertically', self, shortcut='Ctrl+V',
                enabled=False, triggered=self.img_flipv)
        self.resize_act = QtWidgets.QAction('Resize image', self, enabled=False, triggered=self.resize_img)
        self.crop_act = QtWidgets.QAction('Crop image', self, enabled=False, triggered=self.crop_img)
        self.zin_act = QtWidgets.QAction('Zoom &In', self, shortcut='Up', enabled=False, triggered=self.zoom_in)
        self.zout_act = QtWidgets.QAction('Zoom &Out', self, shortcut='Down', enabled=False, triggered=self.zoom_out)
        self.fit_win_act = QtWidgets.QAction('Best &fit', self, checkable=True, shortcut='F',
                enabled=False, triggered=self.zoom_default)
        self.fit_win_act.setChecked(True)
        self.prefs_act = QtWidgets.QAction('Preferences', self, triggered=self.set_prefs)
        self.props_act = QtWidgets.QAction('Properties', self, triggered=self.get_props)
        self.help_act = QtWidgets.QAction('&Help', self, shortcut='F1', triggered=self.help_page)
        self.about_act = QtWidgets.QAction('&About', self, triggered=self.about_cm)
        self.aboutQt_act = QtWidgets.QAction('About &Qt', self,
                triggered=QtWidgets.qApp.aboutQt)

    def create_menu(self):
        acts1 = [self.open_act, self.reload_act, self.print_act, self.save_act, self.props_act, self.exit_act]
        acts2 = [self.rotleft_act, self.rotright_act, self.fliph_act, self.flipv_act, self.resize_act, self.crop_act, self.prefs_act]
        acts3 = [self.next_act, self.prev_act, self.zin_act, self.zout_act, self.fit_win_act, self.fulls_act, self.ss_act, self.ss_next_act]
        acts4 = [self.help_act, self.about_act, self.aboutQt_act]
        fileMenu = self.menuBar().addMenu('File')
        for act in acts1:
            fileMenu.addAction(act)
        editMenu = self.menuBar().addMenu('Edit')
        for act in acts2:
            editMenu.addAction(act)
        viewMenu = self.menuBar().addMenu('View')
        for act in acts3:
            viewMenu.addAction(act)
        helpMenu = self.menuBar().addMenu('Help')
        for act in acts4:
            helpMenu.addAction(act)

        self.action_list = acts1 + acts2 + acts3 + acts4
        for act in self.action_list:
            self.addAction(act)

    def create_dict(self):
        self.orient_dict = {None: self.do_nothing,
                '1': self.do_nothing,
                '2': self.img_fliph,
                '3': self.img_rotate_ud,
                '4': self.img_flipv,
                '5': self.img_rotate_fliph,
                '6': self.img_rotate_right,
                '7': self.img_rotate_flipv,
                '8': self.img_rotate_left}

    def read_prefs(self):
        try:
            conf = preferences.Config()
            values = conf.read_config()
            self.auto_orientation = values[0]
            self.slide_delay = values[1]
            self.quality = values[2]
        except:
            self.auto_orientation = True
            self.slide_delay = 5
            self.quality = 90

    def set_prefs(self):
        dialog = preferences.PrefsDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.auto_orientation = dialog.auto_orientation
            self.slide_delay = dialog.delay_spinb.value()
            self.quality = dialog.qual_spinb.value()
            conf = preferences.Config()
            conf.write_config(self.auto_orientation, self.slide_delay, self.quality)

    def open(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File',
                QtCore.QDir.currentPath())
        if filename:
            if filename[0].lower().endswith(self.readable_list):
                self.open_img(filename[0])
            else:
                QtWidgets.QMessageBox.information(self, 'Error', 'Cannot load {} images.'.format(filename.rsplit('.', 1)[1]))

    def open_img(self, filename):
        self.filename = filename
        self.reload_img()
        dirname = os.path.dirname(self.filename)
        self.set_img_list(dirname)
        self.img_index = self.filelist.index(self.filename)
        if self.action_list:
            for act in self.action_list:
                act.setEnabled(True)
                self.action_list = []

    def set_img_list(self, dirname):
        filelist = os.listdir(dirname)
        self.filelist = [os.path.join(dirname, filename) for filename in filelist
                        if filename.lower().endswith(self.readable_list)]
        self.filelist.sort()
        self.last_file = len(self.filelist) - 1

    def reload_img(self):
        self.scene.clear()
        image = QtGui.QImage(self.filename)
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.load_img()
        self.setWindowTitle(self.filename.rsplit('/', 1)[1])
        if self.auto_orientation:
            try:
                orient = GExiv2.Metadata(self.filename)['Exif.Image.Orientation']
                self.orient_dict[orient]()
            except:
                pass

    def load_img_fit(self):
        self.scene.addPixmap(self.pixmap)
        self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
        self.img_view.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

    def load_img_1to1(self):
        self.img_view.resetTransform()
        self.scene.addPixmap(self.pixmap)
        self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())
        pixitem = QtWidgets.QGraphicsPixmapItem(self.pixmap)
        self.img_view.centerOn(pixitem)

    def go_next_img(self):
        self.img_index = self.img_index + 1 if self.img_index < self.last_file else 0
        self.filename = self.filelist[self.img_index]
        self.reload_img()

    def go_prev_img(self):
        self.img_index = self.img_index - 1 if self.img_index else self.last_file
        self.filename = self.filelist[self.img_index]
        self.reload_img()

    def zoom_default(self):
        if self.fit_win_act.isChecked():
            self.load_img = self.load_img_fit
            self.load_img()
        else:
            self.load_img = self.load_img_1to1
            self.load_img()

    def zoom_in(self):
        self.img_view.zoom(1.1)

    def zoom_out(self):
        self.img_view.zoom(1 / 1.1)

    def img_rotate_left(self):
        self.scene.clear()
        self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(270))
        self.load_img()

    def img_rotate_right(self):
        self.scene.clear()
        self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(90))
        self.load_img()

    def img_fliph(self):
        self.scene.clear()
        self.pixmap = self.pixmap.transformed(QtGui.QTransform().scale(-1, 1))
        self.load_img()

    def img_flipv(self):
        self.scene.clear()
        self.pixmap = self.pixmap.transformed(QtGui.QTransform().scale(1, -1))
        self.load_img()

    def img_rotate_ud(self, button):
        self.scene.clear()
        self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(180))
        self.load_img()

    def img_rotate_fliph(self):
        self.img_rotate_right()
        self.img_fliph()

    def img_rotate_flipv(self):
        self.img_rotate_right()
        self.img_flipv()

    def resize_img(self):
        dialog = editimage.ResizeDialog(self, self.pixmap.width(), self.pixmap.height())
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            width = dialog.get_width.value()
            height = dialog.get_height.value()
            self.pixmap = self.pixmap.scaled(width, height, QtCore.Qt.IgnoreAspectRatio,
                    QtCore.Qt.SmoothTransformation)
            self.save_img()

    def crop_img(self):
        self.img_view.setup_crop(self.pixmap.width(), self.pixmap.height())
        dialog = editimage.CropDialog(self, self.pixmap.width(), self.pixmap.height())
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            coords = self.img_view.get_coords()
            self.pixmap = self.pixmap.copy(*coords)
            self.scene.clear()
            self.load_img()
        self.img_view.rband.hide()

    def toggle_fullscreen(self):
        if self.fulls_act.isChecked():
            self.showFullScreen()
            self.menuBar().hide()
        else:
            self.showNormal()
            self.menuBar().show()

    def toggle_slideshow(self):
        if self.ss_act.isChecked():
            self.showFullScreen()
            self.menuBar().hide()
            self.start_ss()
        else:
            self.toggle_fullscreen()
            self.timer.stop()
            self.ss_timer.stop()

    def start_ss(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_img)
        self.timer.start(self.slide_delay * 1000)
        self.ss_timer = QtCore.QTimer()
        self.ss_timer.timeout.connect(self.update_img)
        self.ss_timer.start(60000)

    def update_img(self):
        if self.slides_next:
            self.go_next_img()
        else:
            self.filename = random.choice(self.filelist)
            self.reload_img()

    def set_slide_type(self):
        self.slides_next = self.ss_next_act.isChecked()

    def inhibit_screensaver(self):
        bus = dbus.SessionBus()
        ss = bus.get_object('org.freedesktop.ScreenSaver','/ScreenSaver')
        self.inhibit_method = ss.get_dbus_method('SimulateUserActivity','org.freedesktop.ScreenSaver')

    def save_img(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save your image', self.filename)
        if filename:
            if filename[0].lower().endswith(self.writeable_list):
                self.pixmap.save(filename[0], None, self.quality)
                exif = GExiv2.Metadata(self.filename)
                if exif:
                    saved_exif = GExiv2.Metadata(filename[0])
                    for tag in exif.get_exif_tags():
                        saved_exif[tag] = exif[tag]
                    saved_exif.set_orientation(GExiv2.Orientation.NORMAL)
                    saved_exif.save_file()
            else:
                QtWidgets.QMessageBox.information(self, 'Error', 'Cannot save {} images.'.format(filename[0].rsplit('.', 1)[1]))

    def print_img(self):
        dialog = QtPrintSupport.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.pixmap.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.pixmap.rect())
            painter.drawPixmap(0, 0, self.pixmap)

    def resizeEvent(self, event=None):
        if self.fit_win_act.isChecked():
            try:
                self.load_img()
            except:
                pass

    def get_props(self):
        image = QtGui.QImage(self.filename)
        preferences.PropsDialog(self, self.filename.rsplit('/', 1)[1], image.width(), image.height())

    def help_page(self):
        preferences.HelpDialog(self)

    def about_cm(self):
        about_message = 'Version: 0.3.1\nAuthor: David Whitlock\nLicense: GPLv3'
        QtWidgets.QMessageBox.about(self, 'About Cheesemaker', about_message)

    def do_nothing(self):
        return

class ImageView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self, parent)

        self.go_prev_img = parent.go_prev_img
        self.go_next_img = parent.go_next_img

        pal = self.palette()
        pal.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(pal)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            x = event.x()
            if x < 100:
                self.go_prev_img()
            elif x > self.width() - 100:
                self.go_next_img()
            else:
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

    def zoom(self, zoomratio):
        self.scale(zoomratio, zoomratio)

    def wheelEvent(self, event):
        zoomratio = 1.1
        if event.angleDelta().y() < 0:
            zoomratio = 1.0 / zoomratio
        self.scale(zoomratio, zoomratio)

    def setup_crop(self, width, height):
        self.rband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        coords = self.mapFromScene(0, 0, width, height)
        self.rband.setGeometry(QtCore.QRect(coords.boundingRect()))
        self.rband.show()

    def crop_draw(self, x, y, width, height):
        coords = self.mapFromScene(x, y, width, height)
        self.rband.setGeometry(QtCore.QRect(coords.boundingRect()))

    def get_coords(self):
        rect = self.rband.geometry()
        size = self.mapToScene(rect).boundingRect()
        x = int(size.x())
        y = int(size.y())
        width = int(size.width())
        height = int(size.height())
        return (x, y, width, height)

class ImageViewer(QtWidgets.QApplication):
    def __init__(self, args):
        QtWidgets.QApplication.__init__(self, args)

        self.args = args
        self.readable_list = ('bmp', 'gif', 'jpg', 'jpeg', 'mng', 'png', 'pbm',
                'pgm', 'ppm', 'tif', 'tiff', 'xbm', 'xpm', 'svg', 'tga')

    def startup(self):
        if len(self.args) > 1:
            files = self.args[1:]
            self.open_files(files)
        else:
            self.open_win(None)

    def open_files(self, files):
        for filename in files:
            if filename.lower().endswith(self.readable_list):
                self.open_win(filename)

    def open_win(self, filename):
        win = MainWindow(self)
        win.show()
        if filename:
            win.open_img(filename)

def main():
    app = ImageViewer(sys.argv)
    app.startup()
    app.exec_()
