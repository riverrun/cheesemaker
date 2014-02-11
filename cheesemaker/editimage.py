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

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QSpinBox, QCheckBox

class SpinBox(QSpinBox):
    def __init__(self, val, maxval, step, func):
        QSpinBox.__init__(self)

        self.setRange(0, maxval)
        self.setValue(val)
        self.setSingleStep(step)
        self.valueChanged.connect(func)

class ResizeDialog(QDialog):
    def __init__(self, parent, width, height):
        QDialog.__init__(self, parent)

        self.setWindowTitle('Resize image')
        self.ratio = width / height
        layout = QGridLayout()
        self.setLayout(layout)

        self.set_resize_view(layout, width, height)
        self.set_aspratio_view(layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(250, 150)
        self.show()

    def set_resize_view(self, layout, width, height):
        layout.addWidget(QLabel('Width'), 0, 0, 1, 1)
        self.get_width = SpinBox(width, width, 10, self.width_changed)
        layout.addWidget(self.get_width, 0, 1, 1, 1)

        layout.addWidget(QLabel('Height'), 1, 0, 1, 1)
        self.get_height = SpinBox(height, height, 10, self.height_changed)
        layout.addWidget(self.get_height, 1, 1, 1, 1)

    def set_aspratio_view(self, layout):
        self.pres_aspratio = True
        self.aspratio = QCheckBox('Preserve aspect ratio')
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
        """Toggle whether aspect ratio should be preserved."""
        self.pres_aspratio = self.aspratio.isChecked()

class CropDialog(QDialog):
    def __init__(self, parent, width, height):
        QDialog.__init__(self, parent)

        self.setWindowTitle('Crop image')
        self.draw = parent.img_view.crop_draw
        self.new_width = self.width = width
        self.new_height = self.height = height

        layout = QGridLayout()
        self.setLayout(layout)
        self.set_crop_view(layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(350, 250)
        self.show()

    def set_crop_view(self, layout):
        layout.addWidget(QLabel('Distance from the left'), 0, 0, 1, 1)
        self.get_lx = SpinBox(0, self.width - 1, 5, self.lx_changed)
        layout.addWidget(self.get_lx, 0, 1, 1, 1)

        layout.addWidget(QLabel('Distance from the right'), 1, 0, 1, 1)
        self.get_rx = SpinBox(0, self.width - 1, 5, self.rx_changed)
        layout.addWidget(self.get_rx, 1, 1, 1, 1)

        layout.addWidget(QLabel('Distance from the top'), 2, 0, 1, 1)
        self.get_ty = SpinBox(0, self.height - 1, 5, self.ty_changed)
        layout.addWidget(self.get_ty, 2, 1, 1, 1)

        layout.addWidget(QLabel('Distance from the bottom'), 3, 0, 1, 1)
        self.get_by = SpinBox(0, self.height - 1, 5, self.by_changed)
        layout.addWidget(self.get_by, 3, 1, 1, 1)

    def lx_changed(self):
        upper = self.width - self.get_lx.value()
        self.get_rx.setMaximum(upper - 1)
        self.new_width = upper - self.get_rx.value()
        self.draw(self.get_lx.value(), self.get_ty.value(), self.new_width, self.new_height)

    def rx_changed(self):
        upper = self.width - self.get_rx.value()
        self.get_lx.setMaximum(upper - 1)
        self.new_width = upper - self.get_lx.value()
        self.draw(self.get_lx.value(), self.get_ty.value(), self.new_width, self.new_height)

    def ty_changed(self):
        upper = self.height - self.get_ty.value()
        self.get_by.setMaximum(upper - 1)
        self.new_height = upper - self.get_by.value()
        self.draw(self.get_lx.value(), self.get_ty.value(), self.new_width, self.new_height)

    def by_changed(self):
        upper = self.height - self.get_by.value()
        self.get_ty.setMaximum(upper - 1)
        self.new_height = upper - self.get_ty.value()
        self.draw(self.get_lx.value(), self.get_ty.value(), self.new_width, self.new_height)
