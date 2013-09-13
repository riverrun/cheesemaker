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

import os
import configparser
from gi.repository import Gtk, Pango

class Config(object):
    def __init__(self):
        config_dir = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
        self.config_dir = os.path.join(config_dir, 'cheesemaker')
        if not os.path.isdir(self.config_dir):
            os.mkdir(self.config_dir)
        self.config_file = os.path.join(self.config_dir, 'cheesemaker.ini')

        self.config = configparser.ConfigParser()

    def read_config(self):
        self.config.read(self.config_file)
        com = self.config['Common']
        orientation = com.getboolean('AutoOrientation')
        bg_color = com['BackgroundColor'].strip('<Gdk.Color>()')
        bg_color = [float(num[-8:]) for num in bg_color.split(',')]
        slide_delay = int(com['SlideTimeDelay'])
        quality = int(com['Quality'])
        recursive = com.getboolean('Recursive')
        return (orientation, bg_color, slide_delay, quality, recursive)

    def write_config(self, orientation, bg_color, slide_delay, quality, recursive):
        self.config['Common'] = {}
        com = self.config['Common']
        com['AutoOrientation'] = str(orientation)
        com['BackgroundColor'] = str(bg_color)
        com['SlideTimeDelay'] = str(slide_delay)
        com['Quality'] = str(quality)
        com['Recursive'] = str(recursive)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

class PrefsDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, 'Preferences', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(300, 250)
        mainbox = self.get_content_area()
        notebk = Gtk.Notebook()
        mainbox.pack_start(notebk, True, True, 0)
        box_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebk.append_page(box_1, None)
        notebk.set_tab_label_text(box_1, 'General')
        box_1.set_border_width(16)

        self.auto_orientation = parent.auto_orientation
        self.bg_color = parent.bg_color
        self.slide_delay = parent.slide_delay

        self.set_orient_view(box_1)
        self.set_color_view(box_1)
        self.set_delay_view(box_1)

        box_2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebk.append_page(box_2, None)
        notebk.set_tab_label_text(box_2, 'Advanced')
        box_2.set_border_width(16)

        self.quality = parent.quality
        self.set_quality_view(box_2)
        self.recursive = parent.recursive
        self.set_subdir_view(box_2)

        self.show_all()

    def bool_view(self, box, title_name, spinb, func, bool_value):
        title = Gtk.Label()
        box.pack_start(title, True, True, 0)
        title.set_markup('<b>' + title_name + '</b>')
        title.set_halign(Gtk.Align.START)
        box.pack_start(spinb, True, True, 0)
        spinb.connect('toggled', func)
        spinb.set_active(bool_value)

    def set_orient_view(self, box):
        spinb = Gtk.CheckButton('Automatic orientation using image data')
        self.bool_view(box, 'Orientation', spinb, self.auto_orient, self.auto_orientation)

    def set_color_view(self, box):
        color_title = Gtk.Label()
        box.pack_start(color_title, True, True, 0)
        color_box = Gtk.Box()
        box.pack_start(color_box, True, True, 0)
        color_title.set_markup('<b>Background color</b>')
        color_title.set_halign(Gtk.Align.START)
        color_label = Gtk.Label('Choose the background color')
        color_box.pack_start(color_label, True, True, 0)
        color_label.set_halign(Gtk.Align.START)
        self.color_button = Gtk.Button()
        self.color_button = Gtk.ColorButton()
        color_box.pack_start(self.color_button, True, True, 0)

    def spinb_view(self, box, title_name, label_name, def_adj, min_adj, max_adj, step, spinb):
        title = Gtk.Label()
        box.pack_start(title, True, True, 0)
        title.set_markup('<b>' + title_name + '</b>')
        title.set_halign(Gtk.Align.START)
        subbox = Gtk.Box()
        box.pack_start(subbox, True, True, 0)
        label = Gtk.Label()
        label.set_markup(label_name)
        label.set_halign(Gtk.Align.START)
        subbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(def_adj, min_adj, max_adj, step, 10, 0)
        spinb.set_adjustment(adjustment)
        spinb.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        subbox.pack_start(spinb, True, True, 0)

    def set_delay_view(self, box):
        self.get_delay = Gtk.SpinButton()
        t_name = 'Slideshow'
        l_name = 'Time between images'
        self.spinb_view(box, t_name, l_name, self.slide_delay, 1, 50, 1, self.get_delay)

    def auto_orient(self, button):
        self.auto_orientation = button.get_active()

    def set_quality_view(self, box):
        self.get_quality = Gtk.SpinButton()
        t_name = 'Jpeg quality'
        l_name = 'Quality of saved Jpeg images'
        self.spinb_view(box, t_name, l_name, self.quality, 25, 100, 5, self.get_quality)

    def set_subdir_view(self, box):
        spinb = Gtk.CheckButton('Include images in subfolders')
        self.bool_view(box, 'Show subfolders', spinb, self.subdir, self.recursive)

    def subdir(self, button):
        self.recursive = button.get_active()

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

        self.set_textview(text)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.add(self.textview)
        box = self.get_content_area()
        box.pack_start(scrolledwindow, True, True, 0)
        self.show_all()

    def set_textview(self, text):
        self.textview = Gtk.TextView()
        fontdesc = Pango.FontDescription('serif')
        self.textview.modify_font(fontdesc)
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        buff = self.textview.get_buffer()
        buff.set_text(text)
        tag_title = buff.create_tag('title', font='sans bold 12')
        tag_subtitle = buff.create_tag('subtitle', font='sans bold')
        self.add_tag(buff, tag_title, 0, 1)
        for startline in (3, 6, 9, 13, 16, 19, 25, 49, 52):
            self.add_tag(buff, tag_subtitle, startline, startline+1)

    def add_tag(self, buffer_name, tag_name, startline, endline):
        start = buffer_name.get_iter_at_line(startline)
        end = buffer_name.get_iter_at_line(endline)
        buffer_name.apply_tag(tag_name, start, end)

class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)

        license = ('Cheesemaker is free software: you can redistribute it and/or modify '
        'it under the terms of the GNU General Public License as published by '
        'the Free Software Foundation, either version 3 of the License, or '
        '(at your option) any later version.\n\n'
        'Cheesemaker is distributed in the hope that it will be useful, '
        'but WITHOUT ANY WARRANTY; without even the implied warranty of '
        'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the '
        'GNU General Public License for more details.\n\n'
        'You should have received a copy of the GNU General Public License '
        'along with Cheesemaker. If not, see http://www.gnu.org/licenses/gpl.html')

        self.set_program_name('Cheesemaker')
        self.set_version('0.2.5')
        self.set_license(license)
        self.set_wrap_license(True)
        self.set_comments('A simple image viewer.')
        self.set_authors(['David Whitlock <alovedalongthe@gmail.com>'])
        self.set_logo_icon_name('cheesemaker')
