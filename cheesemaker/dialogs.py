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

class SlidesDelay(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, 'Set the time between images', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             '_Select', Gtk.ResponseType.OK))

        self.set_default_size(300, 100)
        box = self.get_content_area()
        hbox = Gtk.Box()
        box.pack_start(hbox, True, True, 0)

        slides_delay_label = Gtk.Label('Time between images')
        hbox.pack_start(slides_delay_label, True, True, 0)

        adjustment = Gtk.Adjustment(5, 1, 50, 1, 10, 0)
        self.choose_delay = Gtk.SpinButton()
        self.choose_delay.set_adjustment(adjustment)
        self.choose_delay.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.choose_delay.set_tooltip_text('Choose the time between images')
        hbox.pack_start(self.choose_delay, True, True, 0)
        self.show_all()

