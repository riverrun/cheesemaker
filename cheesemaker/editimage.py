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

    def spinb_view(self, box, name, spinb, adjustment):
        subbox = Gtk.Box()
        box.pack_start(subbox, True, True, 0)
        label = Gtk.Label()
        label.set_markup('<b>' + name + '</b>')
        label.set_halign(Gtk.Align.START)
        subbox.pack_start(label, True, True, 0)

        spinb.set_adjustment(adjustment)
        spinb.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        subbox.pack_start(spinb, True, True, 0)

    def set_resize_view(self, box, width, height):
        self.get_width = Gtk.SpinButton()
        wadj = Gtk.Adjustment(width, 0, width, 1, 10, 0)
        self.spinb_view(box, 'Width', self.get_width, wadj)
        self.width_signal = self.get_width.connect('value-changed', self.width_changed)

        self.get_height = Gtk.SpinButton()
        hadj = Gtk.Adjustment(height, 0, height, 1, 10, 0)
        self.spinb_view(box, 'Height', self.get_height, hadj)
        self.height_signal = self.get_height.connect('value-changed', self.height_changed)

    def set_aspratio_view(self, box):
        self.pres_aspratio = True
        aspratio = Gtk.CheckButton('Preserve aspect ratio')
        box.pack_start(aspratio, True, True, 0)
        aspratio.connect('toggled', self.toggle_aspratio)
        aspratio.set_active(self.pres_aspratio)

    def width_changed(self, spinb):
        width = self.get_width.get_value_as_int()
        if self.pres_aspratio:
            height = width / self.ratio
            with self.get_height.handler_block(self.height_signal):
                self.get_height.set_value(int(height))

    def height_changed(self, spinb):
        height = self.get_height.get_value_as_int()
        if self.pres_aspratio:
            width = height * self.ratio
            with self.get_width.handler_block(self.width_signal):
                self.get_width.set_value(int(width))

    def toggle_aspratio(self, button):
        self.pres_aspratio = button.get_active()

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
