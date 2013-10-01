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

class ResizeDialog(QtGui.QDialog):
    def __init__(self, parent, width, height):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle('Resize image')
        self.ratio = width / height
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        self.set_resize_view(layout, width, height)
        self.set_aspratio_view(layout)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(250, 150)
        self.show()

    def set_resize_view(self, layout, width, height):
        layout.addWidget(QtGui.QLabel('Width'), 0, 0, 1, 1)
        self.get_width = QtGui.QSpinBox()
        self.get_width.setRange(0, width)
        self.get_width.setValue(width)
        self.get_width.setSingleStep(10)
        self.connect(self.get_width, QtCore.SIGNAL('valueChanged(int)'), self.width_changed)
        layout.addWidget(self.get_width, 0, 1, 1, 1)

        layout.addWidget(QtGui.QLabel('Height'), 1, 0, 1, 1)
        self.get_height = QtGui.QSpinBox()
        self.get_height.setRange(0, height)
        self.get_height.setValue(height)
        self.get_height.setSingleStep(10)
        self.connect(self.get_height, QtCore.SIGNAL('valueChanged(int)'), self.height_changed)
        layout.addWidget(self.get_height, 1, 1, 1, 1)

    def set_aspratio_view(self, layout):
        self.pres_aspratio = True
        self.aspratio = QtGui.QCheckBox('Preserve aspect ratio')
        self.aspratio.setChecked(True)
        self.aspratio.toggled.connect(self.toggle_aspratio)
        layout.addWidget(self.aspratio, 2, 0, 1, 2)

    def width_changed(self, value):
        if self.pres_aspratio:
            height = value / self.ratio
            self.get_height.blockSignals(True)
            self.get_height.setValue(height)
            self.get_height.blockSignals(False)

    def height_changed(self, value):
        if self.pres_aspratio:
            width = value * self.ratio
            self.get_width.blockSignals(True)
            self.get_width.setValue(width)
            self.get_width.blockSignals(False)

    def toggle_aspratio(self):
        self.pres_aspratio = self.aspratio.isChecked()

class CropDialog(QtGui.QDialog):
    def __init__(self, parent, width, height):
    #def __init__(self, parent, width, height, pixwidth, pixheight, xoffset, yoffset):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle('Crop image')
        # add signal to connect to rubberband
        self.width = width
        self.height = height
        #self.pixwidth = pixwidth
        #self.pixheight = pixheight
        #self.ratio = self.width / self.pixwidth
        #self.xoffset = xoffset
        #self.yoffset = yoffset

        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        self.set_crop_view(layout)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(350, 250)
        self.show()

    def set_crop_view(self, layout):
        layout.addWidget(QtGui.QLabel('Distance from the left'), 0, 0, 1, 1)
        self.get_lx = QtGui.QSpinBox()
        self.get_lx.setRange(0, self.width - 1)
        self.get_lx.setValue(0)
        self.get_lx.setSingleStep(10)
        self.connect(self.get_lx, QtCore.SIGNAL('valueChanged(int)'), self.lx_changed)
        layout.addWidget(self.get_lx, 0, 1, 1, 1)

        layout.addWidget(QtGui.QLabel('Distance from the right'), 1, 0, 1, 1)
        self.get_rx = QtGui.QSpinBox()
        self.get_rx.setRange(0, self.width - 1)
        self.get_rx.setValue(0)
        self.get_rx.setSingleStep(10)
        self.connect(self.get_rx, QtCore.SIGNAL('valueChanged(int)'), self.rx_changed)
        layout.addWidget(self.get_rx, 1, 1, 1, 1)

        layout.addWidget(QtGui.QLabel('Distance from the top'), 2, 0, 1, 1)
        self.get_ty = QtGui.QSpinBox()
        self.get_ty.setRange(0, self.height - 1)
        self.get_ty.setValue(0)
        self.get_ty.setSingleStep(10)
        self.connect(self.get_ty, QtCore.SIGNAL('valueChanged(int)'), self.ty_changed)
        layout.addWidget(self.get_ty, 2, 1, 1, 1)

        layout.addWidget(QtGui.QLabel('Distance from the bottom'), 3, 0, 1, 1)
        self.get_by = QtGui.QSpinBox()
        self.get_by.setRange(0, self.height - 1)
        self.get_by.setValue(0)
        self.get_by.setSingleStep(10)
        self.connect(self.get_by, QtCore.SIGNAL('valueChanged(int)'), self.by_changed)
        layout.addWidget(self.get_by, 3, 1, 1, 1)

    def lx_changed(self):
        lx = self.get_lx.value() + 1
        upper = self.width - lx
        self.get_rx.setMaximum(upper)
        #self.image.queue_draw()

    def rx_changed(self, spinb):
        rx = self.get_rx.value() + 1
        upper = self.width - rx
        self.get_lx.setMaximum(upper)
        #self.image.queue_draw()

    def ty_changed(self, spinb):
        ty = self.get_ty.value() + 1
        upper = self.width - ty
        self.get_by.setMaximum(upper)
        #self.image.queue_draw()

    def by_changed(self, spinb):
        by = self.get_by.value() + 1
        upper = self.width - by
        self.get_ty.setMaximum(upper)
        #self.image.queue_draw()

    def on_draw(self):
        # draw on image
        pass
