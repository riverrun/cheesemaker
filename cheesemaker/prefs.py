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

import os, configparser
from gi.repository import Gtk, Gdk
from xdg import BaseDirectory

class Config(object):
    def __init__(self):
        self.config_dir = os.path.join(BaseDirectory.xdg_config_home, 'cheesemaker')
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        self.config_file = os.path.join(self.config_dir, 'cheesemaker')
        
class PrefsDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, 'Preferences', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(300, 200)
        box = self.get_content_area()
        box.set_border_width(16)

        self.bg_color = Gdk.RGBA(0.0, 0.0, 0.0, 1.0)

        color_title = Gtk.Label()
        box.pack_start(color_title, True, True, 0)
        color_box = Gtk.Box()
        box.pack_start(color_box, True, True, 0)
        self.set_color_view(color_title, color_box)

        slide_delay_title = Gtk.Label()
        box.pack_start(slide_delay_title, True, True, 0)
        slide_delay_box = Gtk.Box()
        box.pack_start(slide_delay_box, True, True, 0)
        self.set_delay_view(slide_delay_title, slide_delay_box)

        self.show_all()

    def set_color_view(self, color_title, color_box):
        color_title.set_markup('<b>Background color</b>')
        color_title.set_halign(Gtk.Align.START)
        color_label = Gtk.Label('Choose the background color')
        color_box.pack_start(color_label, True, True, 0)
        color_label.set_halign(Gtk.Align.START)
        self.color_button = Gtk.Button()
        self.color_button = Gtk.ColorButton()
        color_box.pack_start(self.color_button, True, True, 0)

    def set_delay_view(self, slide_delay_title, slide_delay_box):
        slide_delay_title.set_markup('<b>Slideshow</b>')
        slide_delay_title.set_halign(Gtk.Align.START)
        slide_delay_label = Gtk.Label('Time between images')
        slide_delay_label.set_halign(Gtk.Align.START)
        slide_delay_box.pack_start(slide_delay_label, True, True, 0)

        adjustment = Gtk.Adjustment(5, 1, 50, 1, 10, 0)
        self.choose_delay = Gtk.SpinButton()
        self.choose_delay.set_adjustment(adjustment)
        self.choose_delay.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.choose_delay.set_tooltip_text('Choose the time between images')
        slide_delay_box.pack_start(self.choose_delay, True, True, 0)

class HelpDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, 'Help page', parent, 0,
            (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))

        self.set_default_size(650, 500)
        self.set_default_response(Gtk.ResponseType.CLOSE)

        try:
            with open('/usr/share/cheesemaker/help_page') as help_file:
                text = help_file.read()
        except:
            with open('/usr/local/share/cheesemaker/help_page') as help_file:
                text = help_file.read()
        label = Gtk.Label()
        label.set_markup(text)
        label.set_line_wrap(True)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add_with_viewport(label)
        box = self.get_content_area()
        box.pack_start(scrolledwindow, True, True, 0)
        self.show_all()

