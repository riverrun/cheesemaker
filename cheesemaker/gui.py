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

from PyQt4 import QtCore, QtGui
from gi.repository import GExiv2
import os
import sys
import dbus
import random
from . import preferences, editimage

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent):
        QtGui.QMainWindow.__init__(self)

        self.printer = QtGui.QPrinter()
        self.create_actions()
        self.create_menu()
        self.create_dict()
        self.load_img = self.load_img_fit
        self.slide_next = True

        self.scene = QtGui.QGraphicsScene()
        self.img_view = ImageView(self)
        self.img_view.setScene(self.scene)
        self.setCentralWidget(self.img_view)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showMenu)

        self.read_prefs()
        self.readable_list = parent.readable_list
        self.writeable_list = ('bmp', 'jpg', 'jpeg', 'png', 'ppm', 'tif', 'tiff', 'xbm', 'xpm')
        self.resize(700, 500)

    def create_actions(self):
        self.open_act = QtGui.QAction('&Open', self, shortcut='Ctrl+O',
                triggered=self.open)
        self.print_act = QtGui.QAction('&Print', self, shortcut='Ctrl+P',
                enabled=False, triggered=self.print_img)
        self.save_act = QtGui.QAction('&Save image', self, shortcut='Ctrl+S',
                enabled=False, triggered=self.save_img)
        self.exit_act = QtGui.QAction('E&xit', self, shortcut='Ctrl+Q',
                triggered=self.close)
        self.fulls_act = QtGui.QAction('Fullscreen', self, shortcut='F11',
                enabled=False, checkable=True, triggered=self.toggle_fullscreen)
        self.ss_act = QtGui.QAction('Slideshow', self, shortcut='F5',
                enabled=False, checkable=True, triggered=self.toggle_slideshow)
        self.ss_next_act = QtGui.QAction('Next / Random image', self, enabled=False,
                checkable=True, triggered=self.set_slide_type)
        self.ss_next_act.setChecked(True)
        self.next_act = QtGui.QAction('Next image', self, shortcut='Right',
                enabled=False, triggered=self.go_next_img)
        self.prev_act = QtGui.QAction('Previous image', self, shortcut='Left',
                enabled=False, triggered=self.go_prev_img)
        self.rotleft_act = QtGui.QAction('Rotate left', self, shortcut='Ctrl+Left',
                enabled=False, triggered=self.img_rotate_left)
        self.rotright_act = QtGui.QAction('Rotate right', self, shortcut='Ctrl+Right',
                enabled=False, triggered=self.img_rotate_right)
        self.fliph_act = QtGui.QAction('Flip image horizontally', self, shortcut='Ctrl+H',
                enabled=False, triggered=self.img_fliph)
        self.flipv_act = QtGui.QAction('Flip image vertically', self, shortcut='Ctrl+V',
                enabled=False, triggered=self.img_flipv)
        self.resize_act = QtGui.QAction('Resize image', self, enabled=False, triggered=self.resize_img)
        self.crop_act = QtGui.QAction('Crop image', self, enabled=False, triggered=self.crop_img)
        self.zin_act = QtGui.QAction('Zoom &In', self, shortcut='Up', enabled=False, triggered=self.zoom_in)
        self.zout_act = QtGui.QAction('Zoom &Out', self, shortcut='Down', enabled=False, triggered=self.zoom_out)
        self.fit_win_act = QtGui.QAction('Best &fit', self, checkable=True, shortcut='F',
                enabled=False, triggered=self.zoom_default)
        self.fit_win_act.setChecked(True)
        self.prefs_act = QtGui.QAction('Preferences', self, triggered=self.set_prefs)
        self.help_act = QtGui.QAction('&Help', self, shortcut='F1', triggered=self.help_page)
        self.about_act = QtGui.QAction('&About', self, triggered=self.about_cm)
        self.aboutQt_act = QtGui.QAction('About &Qt', self,
                triggered=QtGui.qApp.aboutQt)

    def create_menu(self):
        self.popup = QtGui.QMenu(self)
        acts1 = [self.open_act, self.print_act, self.save_act, self.fulls_act, self.next_act, self.prev_act]
        acts2 = [self.zin_act, self.zout_act, self.fit_win_act]
        acts3 = [self.rotleft_act, self.rotright_act, self.fliph_act, self.flipv_act]
        acts4 = [self.resize_act, self.crop_act]
        acts5 = [self.ss_act, self.ss_next_act]
        acts6 = [self.prefs_act, self.help_act, self.about_act, self.aboutQt_act, self.exit_act]
        for act in acts1:
            self.popup.addAction(act)
        zoom_menu = QtGui.QMenu(self.popup)
        zoom_menu.setTitle('Zoom')
        for act in acts2:
            zoom_menu.addAction(act)
        self.popup.addMenu(zoom_menu)
        edit_menu = QtGui.QMenu(self.popup)
        edit_menu.setTitle('Edit')
        for act in acts3:
            edit_menu.addAction(act)
        self.popup.addMenu(edit_menu)
        edit_menu.addSeparator()
        for act in acts4:
            edit_menu.addAction(act)
        slides_menu = QtGui.QMenu(self.popup)
        slides_menu.setTitle('Slideshow')
        for act in acts5:
            slides_menu.addAction(act)
        self.popup.addMenu(slides_menu)
        for act in acts6:
            self.popup.addAction(act)

        self.action_list = acts1 + acts2 + acts3 + acts4 + acts5 + acts6
        for act in self.action_list:
            self.addAction(act)

    def showMenu(self, pos):
        self.popup.popup(self.mapToGlobal(pos))
 
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
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.auto_orientation = dialog.auto_orientation
            self.slide_delay = dialog.delay_spinb.value()
            self.quality = dialog.qual_spinb.value()
            conf = preferences.Config()
            conf.write_config(self.auto_orientation, self.slide_delay, self.quality)

    def open(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File',
                QtCore.QDir.currentPath())
        if filename:
            if filename.lower().endswith(self.readable_list):
                self.open_img(filename)
            else:
                QtGui.QMessageBox.information(self, 'Error', 'Cannot load {} images.'.format(filename.rsplit('.', 1)[1]))

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
        self.img_view.resetMatrix()
        self.scene.addPixmap(self.pixmap)
        pixitem = QtGui.QGraphicsPixmapItem(self.pixmap)
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
        if dialog.exec_() == QtGui.QDialog.Accepted:
            width = dialog.get_width.value()
            height = dialog.get_height.value()
            self.pixmap = self.pixmap.scaled(width, height, QtCore.Qt.IgnoreAspectRatio,
                    QtCore.Qt.SmoothTransformation)
            self.save_img()

    def crop_img(self):
        dialog = editimage.CropDialog(self, self.pixmap.width(), self.pixmap.height())
        if dialog.exec_() == QtGui.QDialog.Accepted:
            print(dialog.get_lx.value())

    def toggle_fullscreen(self):
        if self.fulls_act.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_slideshow(self):
        if self.ss_act.isChecked():
            self.showFullScreen()
            self.start_ss()
        else:
            self.toggle_fullscreen()
            self.timer.stop()
            self.ss_timer.stop()

    def start_ss(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_img)
        self.timer.start(self.delay * 1000)
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

    def save_img(self): # Need to rewrite exif data
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save your image',
                self.filename)
        if filename:
            if filename.lower().endswith(self.writeable_list):
                self.pixmap.save(filename, None, self.quality)
            else:
                QtGui.QMessageBox.information(self, 'Error', 'Cannot save {} images.'.format(filename.rsplit('.', 1)[1]))

    def print_img(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
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

    def help_page(self):
        preferences.HelpDialog(self)

    def about_cm(self):
        about_message = 'Version: 0.3.0\nAuthor: David Whitlock\nLicense: GPLv3'
        QtGui.QMessageBox.about(self, 'About Cheesemaker', about_message)

    def do_nothing(self):
        return

class ImageView(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)

        self.load_img = parent.load_img
        self.go_prev_img = parent.go_prev_img
        self.go_next_img = parent.go_next_img

        pal = self.palette()
        pal.setColor(self.backgroundRole(), QtCore.Qt.black)
        self.setPalette(pal)
        self.setFrameShape(QtGui.QFrame.NoFrame)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            x = event.x()
            if x < 100:
                self.go_prev_img()
            elif x > self.width() - 100:
                self.go_next_img()
            else:
                self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
        QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def zoom(self, zoomratio):
        self.scale(zoomratio, zoomratio)

    def wheelEvent(self,  event):
        zoomratio = 1.1
        if event.delta() < 0:
            zoomratio = 1.0 / zoomratio
        self.scale(zoomratio, zoomratio)

class ImageViewer(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)

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
