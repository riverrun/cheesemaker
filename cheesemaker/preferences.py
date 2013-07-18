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
        recursive = com.getboolean('Recursive')
        quality = int(com['Quality'])
        rem_exif_data = com.getboolean('RemExifData')
        return (orientation, bg_color, slide_delay, recursive, quality, rem_exif_data)

    def write_config(self, orientation, bg_color, slide_delay, recursive, quality, rem_exif_data):
        self.config['Common'] = {}
        com = self.config['Common']
        com['AutoOrientation'] = str(orientation)
        com['BackgroundColor'] = str(bg_color)
        com['SlideTimeDelay'] = str(slide_delay)
        com['Recursive'] = str(recursive)
        com['Quality'] = str(quality)
        com['RemExifData'] = str(rem_exif_data)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

class PrefsDialog(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, 'Preferences', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(300, 300)
        mainbox = self.get_content_area()
        notebk = Gtk.Notebook()
        mainbox.pack_start(notebk, True, True, 0)
        box_1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebk.append_page(box_1, None)
        notebk.set_tab_label_text(box_1, 'General')
        box_1.set_border_width(16)

        self.auto_orientation = parent.auto_orientation
        self.bg_color = Gdk.RGBA(0.0, 0.0, 0.0, 1.0)
        self.slide_delay = parent.slide_delay
        self.recursive = parent.recursive

        self.set_orient_view(box_1)
        self.set_color_view(box_1)
        self.set_delay_view(box_1)
        self.set_subdir_view(box_1)

        box_2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        notebk.append_page(box_2, None)
        notebk.set_tab_label_text(box_2, 'Save options')
        box_2.set_border_width(16)

        self.quality = parent.quality
        self.rem_exif_data = parent.rem_exif_data

        self.set_quality_view(box_2)
        self.set_exif_handling(box_2)

        self.show_all()

    def set_orient_view(self, box):
        orient_title = Gtk.Label()
        box.pack_start(orient_title, True, True, 0)
        orient_button = Gtk.CheckButton('Automatic orientation using image data')
        box.pack_start(orient_button, True, True, 0)
        orient_title.set_markup('<b>Orientation</b>')
        orient_title.set_halign(Gtk.Align.START)
        orient_button.connect('toggled', self.auto_orient)
        orient_button.set_active(self.auto_orientation)

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

    def set_delay_view(self, box):
        slide_delay_title = Gtk.Label()
        box.pack_start(slide_delay_title, True, True, 0)
        slide_delay_box = Gtk.Box()
        box.pack_start(slide_delay_box, True, True, 0)
        slide_delay_title.set_markup('<b>Slideshow</b>')
        slide_delay_title.set_halign(Gtk.Align.START)
        slide_delay_label = Gtk.Label('Time between images')
        slide_delay_label.set_halign(Gtk.Align.START)
        slide_delay_box.pack_start(slide_delay_label, True, True, 0)

        adjustment = Gtk.Adjustment(self.slide_delay, 1, 50, 1, 10, 0)
        self.choose_delay = Gtk.SpinButton()
        self.choose_delay.set_adjustment(adjustment)
        self.choose_delay.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.choose_delay.set_tooltip_text('Choose the time between images')
        slide_delay_box.pack_start(self.choose_delay, True, True, 0)

    def set_subdir_view(self, box):
        subdir_title = Gtk.Label()
        box.pack_start(subdir_title, True, True, 0)
        subdir_button = Gtk.CheckButton('Include images in subfolders')
        box.pack_start(subdir_button, True, True, 0)
        subdir_title.set_markup('<b>Show subfolders</b>')
        subdir_title.set_halign(Gtk.Align.START)
        subdir_button.connect('toggled', self.subdir)
        subdir_button.set_active(self.recursive)

    def auto_orient(self, button):
        self.auto_orientation = button.get_active()

    def subdir(self, button):
        self.recursive = button.get_active()

    def set_quality_view(self, box):
        quality_title = Gtk.Label()
        box.pack_start(quality_title, True, True, 0)
        quality_box = Gtk.Box()
        box.pack_start(quality_box, True, True, 0)
        quality_title.set_markup('<b>Jpeg quality</b>')
        quality_title.set_halign(Gtk.Align.START)
        quality_label = Gtk.Label('Quality of saved Jpeg images')
        quality_label.set_halign(Gtk.Align.START)
        quality_box.pack_start(quality_label, True, True, 0)

        adjustment = Gtk.Adjustment(self.quality, 25, 100, 5, 10, 0)
        self.choose_quality = Gtk.SpinButton()
        self.choose_quality.set_adjustment(adjustment)
        self.choose_quality.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        quality_box.pack_start(self.choose_quality, True, True, 0)

    def set_exif_handling(self, box):
        exif_title = Gtk.Label()
        box.pack_start(exif_title, True, True, 0)
        exif_button = Gtk.CheckButton('Remove Exif data when saving images')
        box.pack_start(exif_button, True, True, 0)
        exif_title.set_markup('<b>Exif data handling</b>')
        exif_title.set_halign(Gtk.Align.START)
        exif_button.connect('toggled', self.rem_exif)
        exif_button.set_active(self.rem_exif_data)
        exif_button.set_sensitive(False)
        exif_button.set_tooltip_text('Sorry, not finished yet')

    def rem_exif(self, button):
        self.rem_exif_data = button.get_active()

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
        self.set_version('0.2.2')
        self.set_license(license)
        self.set_wrap_license(True)
        self.set_comments('A simple image viewer.')
        self.set_authors(['David Whitlock <alovedalongthe@gmail.com>'])
        self.set_logo_icon_name('cheesemaker')
