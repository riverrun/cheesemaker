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

from gi.repository import Gtk

class ResizeDialog(Gtk.Dialog):
    def __init__(self, parent, width, height):
        Gtk.Dialog.__init__(self, 'Resize image', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.ratio = width / height
        self.set_default_size(250, 200)
        box = self.get_content_area()
        box.set_border_width(16)
        resize_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(resize_box, True, True, 0)
        self.set_resize_view(resize_box, width, height)
        self.set_aspratio_view(resize_box)
        self.show_all()

    def spinb_view(self, box, name, def_adj, max_adj, spinb):
        subbox = Gtk.Box()
        box.pack_start(subbox, True, True, 0)
        label = Gtk.Label()
        label.set_markup('<b>' + name + '</b>')
        label.set_halign(Gtk.Align.START)
        subbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(def_adj, 0, max_adj, 1, 10, 0)
        spinb.set_adjustment(adjustment)
        spinb.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        subbox.pack_start(spinb, True, True, 0)

    def set_resize_view(self, box, width, height):
        self.choose_width = Gtk.SpinButton()
        self.spinb_view(box, 'Width', width, width, self.choose_width)
        self.width_signal = self.choose_width.connect('value-changed', self.width_changed)

        self.choose_height = Gtk.SpinButton()
        self.spinb_view(box, 'Height', height, height, self.choose_height)
        self.height_signal = self.choose_height.connect('value-changed', self.height_changed)

    def set_aspratio_view(self, box):
        self.pres_aspratio = True
        aspratio = Gtk.CheckButton('Preserve aspect ratio')
        box.pack_start(aspratio, True, True, 0)
        aspratio.connect('toggled', self.toggle_aspratio)
        aspratio.set_active(self.pres_aspratio)

    def width_changed(self, spinb):
        width = self.choose_width.get_value_as_int()
        if self.pres_aspratio:
            height = width / self.ratio
            with self.choose_height.handler_block(self.height_signal):
                self.choose_height.set_value(int(height))

    def height_changed(self, spinb):
        height = self.choose_height.get_value_as_int()
        if self.pres_aspratio:
            width = height * self.ratio
            with self.choose_width.handler_block(self.width_signal):
                self.choose_width.set_value(int(width))

    def toggle_aspratio(self, button):
        self.pres_aspratio = button.get_active()

class CropDialog(ResizeDialog):
    def __init__(self, parent, width, height):
        Gtk.Dialog.__init__(self, 'Crop image', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(250, 200)
        box = self.get_content_area()
        box.set_border_width(16)
        crop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(crop_box, True, True, 0)
        self.set_xy_view(crop_box, width, height)
        self.set_resize_view(crop_box, width, height)
        self.show_all()

    def set_xy_view(self, box, width, height):
        self.choose_x = Gtk.SpinButton()
        self.spinb_view(box, 'X', 0, width, self.choose_x)
        self.x_signal = self.choose_x.connect('value-changed', self.x_changed)

        self.choose_y = Gtk.SpinButton()
        self.spinb_view(box, 'Y', 0, height, self.choose_y)
        self.y_signal = self.choose_y.connect('value-changed', self.y_changed)

    def width_changed(self, spinb):
        pass

    def height_changed(self, spinb):
        pass

    def x_changed(self, spinb):
        pass

    def y_changed(self, spinb):
        pass
