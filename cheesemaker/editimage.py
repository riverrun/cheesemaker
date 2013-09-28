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

class CropDialog(ResizeDialog):
    def __init__(self, parent, width, height, pixwidth, pixheight, xoffset, yoffset):
        Gtk.Dialog.__init__(self, 'Crop image', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.image = parent.image
        self.draw_signal = self.image.connect_after('draw', self.on_draw)
        self.width = width
        self.height = height
        self.pixwidth = pixwidth
        self.pixheight = pixheight
        self.ratio = self.width / self.pixwidth
        self.xoffset = xoffset
        self.yoffset = yoffset

        self.set_default_size(300, 200)
        box = self.get_content_area()
        box.set_border_width(16)
        crop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(crop_box, True, True, 0)
        self.set_crop_view(crop_box)
        self.show_all()

    def set_crop_view(self, box):
        self.get_lx = Gtk.SpinButton()
        self.lx_adj = Gtk.Adjustment(0, 0, self.width - 1, 10, 100, 0)
        self.spinb_view(box, 'Distance from the left', self.get_lx, self.lx_adj)
        self.lx_signal = self.get_lx.connect('value-changed', self.lx_changed)

        self.get_rx = Gtk.SpinButton()
        self.rx_adj = Gtk.Adjustment(0, 0, self.width - 1, 10, 100, 0)
        self.spinb_view(box, 'Distance from the right', self.get_rx, self.rx_adj)
        self.rx_signal = self.get_rx.connect('value-changed', self.rx_changed)

        self.get_ty = Gtk.SpinButton()
        self.ty_adj = Gtk.Adjustment(0, 0, self.height - 1, 10, 100, 0)
        self.spinb_view(box, 'Distance from the top', self.get_ty, self.ty_adj)
        self.ty_signal = self.get_ty.connect('value-changed', self.ty_changed)

        self.get_by = Gtk.SpinButton()
        self.by_adj = Gtk.Adjustment(0, 0, self.height - 1, 10, 100, 0)
        self.spinb_view(box, 'Distance from the bottom', self.get_by, self.by_adj)
        self.by_signal = self.get_by.connect('value-changed', self.by_changed)

    def lx_changed(self, spinb):
        lx = self.get_lx.get_value_as_int() + 1
        upper = self.width - lx
        self.rx_adj.set_upper(upper)
        self.image.queue_draw()

    def rx_changed(self, spinb):
        rx = self.get_rx.get_value_as_int() + 1
        upper = self.width - rx
        self.lx_adj.set_upper(upper)
        self.image.queue_draw()

    def ty_changed(self, spinb):
        ty = self.get_ty.get_value_as_int() + 1
        upper = self.height - ty
        self.by_adj.set_upper(upper)
        self.image.queue_draw()

    def by_changed(self, spinb):
        by = self.get_by.get_value_as_int() + 1
        upper = self.height - by
        self.ty_adj.set_upper(upper)
        self.image.queue_draw()

    def on_draw(self, win, cr):
        x = (self.get_lx.get_value_as_int() / self.ratio)
        y = (self.get_ty.get_value_as_int() / self.ratio)
        width = self.pixwidth - (x + (self.get_rx.get_value_as_int() / self.ratio))
        height = self.pixheight - (y + (self.get_by.get_value_as_int() / self.ratio))
        cr.set_source_rgb(1.0, 0.0, 0.0)
        cr.rectangle(x + self.xoffset, y + self.yoffset, width, height)
        cr.set_line_width(1)
        cr.stroke()
