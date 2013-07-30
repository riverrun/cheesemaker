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

        self.set_default_size(250, 200)
        box = self.get_content_area()
        box.set_border_width(16)
        self.set_resize_view(box, width, height)
        self.show_all()

    def set_resize_view(self, box, width, height):
        self.ratio = width / height
        resize_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(resize_box, True, True, 0)

        width_box = Gtk.Box()
        resize_box.pack_start(width_box, True, True, 0)
        width_label = Gtk.Label()
        width_label.set_markup('<b>Width</b>')
        width_label.set_halign(Gtk.Align.START)
        width_box.pack_start(width_label, True, True, 0)

        adjustment = Gtk.Adjustment(width, 1, width, 1, 10, 0)
        self.choose_width = Gtk.SpinButton()
        self.choose_width.set_adjustment(adjustment)
        self.choose_width.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        width_box.pack_start(self.choose_width, True, True, 0)
        self.width_signal = self.choose_width.connect('value-changed', self.width_changed)

        height_box = Gtk.Box()
        resize_box.pack_start(height_box, True, True, 0)
        height_label = Gtk.Label()
        height_label.set_markup('<b>Height</b>')
        height_label.set_halign(Gtk.Align.START)
        height_box.pack_start(height_label, True, True, 0)

        adjustment = Gtk.Adjustment(height, 1, height, 1, 10, 0)
        self.choose_height = Gtk.SpinButton()
        self.choose_height.set_adjustment(adjustment)
        self.choose_height.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        height_box.pack_start(self.choose_height, True, True, 0)
        self.height_signal = self.choose_height.connect('value-changed', self.height_changed)

        self.pres_aspratio = True
        aspratio = Gtk.CheckButton('Preserve aspect ratio')
        resize_box.pack_start(aspratio, True, True, 0)
        aspratio.connect('toggled', self.toggle_aspratio)
        aspratio.set_active(self.pres_aspratio)

    def width_changed(self, spinb):
        width = self.choose_width.get_value_as_int()
        if self.pres_aspratio:
            height = width / self.ratio
            with self.choose_height.handler_block(self.height_signal):
                self.choose_height.set_value(int(height))
            #self.choose_height.handler_unblock(self.height_signal)

    def height_changed(self, spinb):
        height = self.choose_height.get_value_as_int()
        if self.pres_aspratio:
            width = height * self.ratio
            with self.choose_width.handler_block(self.width_signal):
                self.choose_width.set_value(int(width))
            #self.choose_width.handler_unblock(self.width_signal)

    def toggle_aspratio(self, button):
        self.pres_aspratio = button.get_active()
