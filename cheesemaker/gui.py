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

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import os, random
from . import prefs

ui_info = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='Open'/>
      <menuitem action='Opendir'/>
      <separator/>
      <menuitem action='Saveas'/>
      <separator/>
      <menuitem action='Quit'/>
    </menu>
    <menu action='EditMenu'>
      <menuitem action='Rotateleft'/>
      <menuitem action='Rotateright'/>
      <separator/>
      <menuitem action='Fliphoriz'/>
      <menuitem action='Flipvert'/>
      <separator/>
      <menuitem action='Desaturate'/>
      <separator/>
      <menuitem action='Prefs'/>
    </menu>
    <menu action='ViewMenu'>
      <menuitem action='Nextimg'/>
      <menuitem action='Previmg'/>
      <separator/>
      <menuitem action='ShowMenuBar'/>
      <menuitem action='ShowToolBar'/>
      <separator/>
      <menuitem action='Full'/>
      <menuitem action='Slides'/>
      <menu action='SlidesOpts'>
        <menuitem action='NextSlides'/>
        <menuitem action='RandomSlides'/>
      </menu>
      <separator/>
      <menu action='ZoomMenu'>
        <menuitem action='Zoomin'/>
        <menuitem action='Zoomout'/>
        <menuitem action='Zoom1to1'/>
        <menuitem action='Zoomfit'/>
      </menu>
    </menu>
    <menu action='HelpMenu'>
      <menuitem action='Help'/>
      <menuitem action='About'/>
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='Open'/>
    <separator action='Sep1'/>
    <toolitem action='Previmg'/>
    <toolitem action='Nextimg'/>
    <separator action='Sep2'/>
    <toolitem action='Zoomin'/>
    <toolitem action='Zoomout'/>
    <toolitem action='Zoom1to1'/>
    <toolitem action='Zoomfit'/>
    <separator action='Sep3'/>
    <toolitem action='Help'/>
  </toolbar>
  <popup name='PopupMenu'>
    <menuitem action='Open'/>
    <menuitem action='Opendir'/>
    <separator/>
    <menuitem action='Nextimg'/>
    <menuitem action='Previmg'/>
    <separator/>
    <menuitem action='Full'/>
    <menuitem action='Slides'/>
    <menu action='SlidesOpts'>
      <menuitem action='NextSlides'/>
      <menuitem action='RandomSlides'/>
    </menu>
    <separator/>
    <menuitem action='ShowMenuBar'/>
    <menuitem action='ShowToolBar'/>
    <separator/>
    <menuitem action='Rotateleft'/>
    <menuitem action='Rotateright'/>
    <separator/>
    <menuitem action='Fliphoriz'/>
    <menuitem action='Flipvert'/>
    <separator/>
    <menuitem action='Desaturate'/>
  </popup>
</ui>
"""

class Imagewindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='Cheesemaker')

        self.set_default_size(700, 500)
        self.set_default_icon_name('cheesemaker')
        self.image = Gtk.Image()
        self.image.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 1.0))
        self.image_size = 'Zoomfit'
        self.load_image = self.load_image_fit
        self.win_width = 0
        self.win_height = 0

        self.grid = Gtk.Grid()
        self.add(self.grid)

        action_group = Gtk.ActionGroup('gui_actions')
        self.actions(action_group)
        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)
        self.menubar = uimanager.get_widget('/MenuBar')
        self.grid.attach(self.menubar, 0, 0, 1, 1)
        self.toolbar = uimanager.get_widget('/ToolBar')
        self.grid.attach(self.toolbar, 0, 1, 1, 1)
        self.imageview()

        self.showmenubar = True
        self.showtoolbar = True
        self.slideshow_type = 'NextSlides'
        self.slide_delay = 5
        self.auto_orientation = True

        popup = uimanager.get_widget('/PopupMenu')
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.STRUCTURE_MASK)
        self.connect('button-press-event', self.on_button_press, popup)

        graylist = ['/MenuBar/EditMenu/Desaturate', '/PopupMenu/Desaturate']
        self.graylist = [uimanager.get_widget(name) for name in graylist]
        self.new_image_reset()

        self.format_list = ['ras', 'tif', 'tiff', 'wmf', 'icns', 'ico', 'png', 'wbmp', 
                'gif', 'pnm', 'tga', 'ani', 'xbm', 'xpm', 'jpg', 'pcx', 'jpeg', 'bmp', 'svg']

    def actions(self, action_group):
        action_group.add_actions([
            ('FileMenu', None, '_File'),
            ('Open', Gtk.STOCK_OPEN, '_Open image', None, 'Open image', self.open_image),
            ('Opendir', None, 'Open fol_der', '<Ctrl>D', 'Open folder', self.open_dir),
            ('Saveas', Gtk.STOCK_SAVE, '_Save image', None, 'Save image', self.save_image),
            ('EditMenu', None, '_Edit'),
            ('Rotateleft', None, 'Rotate _left', '<Ctrl>Left', 'Rotate left', self.image_rotate_left),
            ('Rotateright', None, 'Rotate _right', '<Ctrl>Right', 'Rotate right', self.image_rotate_right),
            ('Fliphoriz', None, 'FLip _horizontally', '<Ctrl>H', 'Flip horizontally', self.image_flip_horiz),
            ('Flipvert', None, 'FLip _vertically', '<Ctrl>V', 'Flip vertically', self.image_flip_vert),
            ('Prefs', None, 'Preferences', '<Ctrl>P', 'Preferences', self.set_preferences),
            ('ViewMenu', None, '_View'),
            ('Nextimg', Gtk.STOCK_GO_FORWARD, '_Next image', '<Alt>Right', 'Next image', self.go_next_image),
            ('Previmg', Gtk.STOCK_GO_BACK, '_Previous image', '<Alt>Left', 'Previous image', self.go_prev_image),
            ('SlidesOpts', None, 'S_lideshow options'),
            ('ZoomMenu', None, '_Zoom'),
            ('Zoomin', Gtk.STOCK_ZOOM_IN, 'Zoom in', '<Ctrl>Up', 'Zoom in', self.image_zoom_in),
            ('Zoomout', Gtk.STOCK_ZOOM_OUT, 'Zoom out', '<Ctrl>Down', 'Zoom out', self.image_zoom_out),
            ('HelpMenu', None, '_Help'),
            ('Help', Gtk.STOCK_HELP, 'Help', 'F1', 'Open the help page', self.help_page),
            ('About', Gtk.STOCK_ABOUT, 'About', None, 'About', self.about_dialog),
            ('Quit', Gtk.STOCK_QUIT, 'Quit', None, 'Quit', self.quit_app)
            ])

        action_group.add_toggle_actions([
            ('Desaturate', None, 'Toggle _grayscale', None, 'Toggle grayscale', self.toggle_gray),
            ('Full', Gtk.STOCK_FULLSCREEN, '_Fullscreen', 'F11', 'Fullscreen', self.toggle_full),
            ('Slides', None, '_Slideshow', 'F5', 'Slideshow', self.toggle_slides),
            ('ShowMenuBar', None, 'Show _menubar', None, 'Show menubar', self.toggle_menu, True),
            ('ShowToolBar', None, 'Show _toolbar', None, 'Show toolbar', self.toggle_tool, True)
            ])

        action_group.add_radio_actions([
            ('NextSlides', None, '_Next image', None, 'Next image', 1),
            ('RandomSlides', None, '_Random image', None, 'Random image', 0)
            ], 1, self.slideshow_options)

        action_group.add_radio_actions([
            ('Zoom1to1', Gtk.STOCK_ZOOM_100, 'Normal size', 'N', 'Normal (original) size', 1),
            ('Zoomfit', Gtk.STOCK_ZOOM_FIT, 'Best fit', 'F', 'Best fit', 0)
            ], 0, self.default_zoom_ratio)

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(ui_info)
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def imageview(self):
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)
        self.scrolledwindow.connect('size-allocate', self.on_resize)
        self.grid.attach(self.scrolledwindow, 0, 2, 1, 1)
        self.scrolledwindow.add_with_viewport(self.image)

    def set_preferences(self, button):
        dialog = prefs.PrefsDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.auto_orientation = dialog.auto_orientation
            self.image.override_background_color(Gtk.StateType.NORMAL, dialog.color_button.get_rgba())
            self.slide_delay = dialog.choose_delay.get_value_as_int()
        dialog.destroy()

    def toggle_slides(self, button):
        if button.get_active():
            self.set_fullscreen()
            self.timer_delay = GLib.timeout_add_seconds(self.slide_delay, self.start_slideshow)
        else:
            GLib.source_remove(self.timer_delay)
            self.set_unfullscreen()

    def start_slideshow(self):
        if self.slideshow_type:
            self.go_next_image(None)
        else:
            self.filename = random.choice(self.filelist)
            self.load_image()
            self.image.set_from_pixbuf(self.pixbuf)
        return True

    def slideshow_options(self, button, current):
        self.slideshow_type = current.get_current_value()

    def toggle_full(self, button):
        if button.get_active():
            self.set_fullscreen()
        else:
            self.set_unfullscreen()

    def set_fullscreen(self):
        self.fullscreen()
        self.menubar.hide()
        self.toolbar.hide()
        cursor = Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
        self.get_window().set_cursor(cursor)

    def set_unfullscreen(self):
        self.unfullscreen()
        if self.showmenubar:
            self.menubar.show()
        if self.showtoolbar:
            self.toolbar.show()
        cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
        self.get_window().set_cursor(cursor)

    def toggle_menu(self, button):
        if button.get_active():
            self.menubar.show()
            self.showmenubar = True
        else:
            self.menubar.hide()
            self.showmenubar = False

    def toggle_tool(self, button):
        if button.get_active():
            self.toolbar.show()
            self.showtoolbar = True
        else:
            self.toolbar.hide()
            self.showtoolbar = False

    def toggle_gray(self, button):
        if button.get_active():
            self.pixbuf.saturate_and_pixelate(self.pixbuf, 0.0, False)
            self.grays = True
        else:
            self.grays = False
            self.load_image()
        self.image.set_from_pixbuf(self.pixbuf)

    def load_image_fit(self):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.win_width, self.win_height)
        self.img_width = self.pixbuf.get_width()
        self.img_height = self.pixbuf.get_height()

    def load_image_1to1(self):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        self.img_width = self.pixbuf.get_width()
        self.img_height = self.pixbuf.get_height()

    def apply_orientation(self):
        orient = self.pixbuf.get_option('orientation')
        if orient and int(orient) > 4:
            if int(orient) == 8:
                self.image_rotate_left(None)
            else:
                self.image_rotate_right(None)

    def default_zoom_ratio(self, button, current):
        self.image_size = current.get_name()
        if self.image_size == 'Zoomfit':
            self.load_image = self.load_image_fit
        else:
            self.load_image = self.load_image_1to1
        self.load_image()
        self.pixbuf = self.rotated_flipped(self.pixbuf)
        self.image.set_from_pixbuf(self.pixbuf)

    def image_zoom_in(self, button):
        self.image_zoom(1.25)

    def image_zoom_out(self, button):
        self.image_zoom(0.8)

    def image_zoom(self, zoomratio):
        self.img_width, self.img_height = self.img_width*zoomratio, self.img_height*zoomratio
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_width, self.img_height)
        self.pixbuf = self.rotated_flipped(pixbuf)
        self.image.set_from_pixbuf(self.pixbuf)

    def go_next_image(self, button):
        if self.image_index < len(self.filelist)-1:
            self.image_index += 1
        else:
            self.image_index = 0
        self.new_image_reset()
        self.filename = self.filelist[self.image_index]
        self.load_image()
        if self.auto_orientation:
            self.apply_orientation()
        self.image.set_from_pixbuf(self.pixbuf)

    def go_prev_image(self, button):
        if self.image_index > 0:
            self.image_index -= 1
        else:
            self.image_index = len(self.filelist)-1
        self.new_image_reset()
        self.filename = self.filelist[self.image_index]
        self.load_image()
        if self.auto_orientation:
            self.apply_orientation()
        self.image.set_from_pixbuf(self.pixbuf)

    def image_rotate_left(self, button):
        if self.rotate_state > 0:
            self.rotate_state -= 1
        else:
            self.rotate_state = 3
        if self.rotate_state % 2:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_height, self.img_width)
        else:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_width, self.img_height)
        self.pixbuf = self.rotated_flipped(self.pixbuf)
        self.image.set_from_pixbuf(self.pixbuf)

    def image_rotate_right(self, button):
        if self.rotate_state < 3:
            self.rotate_state += 1
        else:
            self.rotate_state = 0
        if self.rotate_state % 2:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_height, self.img_width)
        else:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_width, self.img_height)
        self.pixbuf = self.rotated_flipped(self.pixbuf)
        self.image.set_from_pixbuf(self.pixbuf)

    def image_flip_horiz(self, button):
        self.pixbuf = self.pixbuf.flip(True)
        self.image.set_from_pixbuf(self.pixbuf)
        self.fliph = not self.fliph

    def image_flip_vert(self, button):
        self.pixbuf = self.pixbuf.flip(False)
        self.image.set_from_pixbuf(self.pixbuf)
        self.flipv = not self.flipv

    def rotated_flipped(self, pixbuf):
        if self.rotate_state:
            if self.rotate_state == 1:
                pixbuf = pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
            elif self.rotate_state == 2:
                pixbuf = pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
            else:
                pixbuf = pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)
        if self.fliph:
            pixbuf = pixbuf.flip(True)
        if self.flipv:
            pixbuf = pixbuf.flip(False)
        if self.grays:
            pixbuf.saturate_and_pixelate(pixbuf, 0.0, False)
        return pixbuf

    def new_image_reset(self):
        self.rotate_state = 0
        self.fliph = False
        self.flipv = False
        self.grays = False
        for name in self.graylist:
            name.set_active(False)

    def open_image(self, button):
        dialog = Gtk.FileChooserDialog('Please choose a file', self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        filefilter = Gtk.FileFilter()
        filefilter.add_pixbuf_formats()
        dialog.set_filter(filefilter)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.filename = dialog.get_filename()
        else:
            dialog.destroy()
            return 0
        dialog.destroy()
        self.new_image_reset()
        self.load_image()
        if self.auto_orientation:
            self.apply_orientation()
        self.image.set_from_pixbuf(self.pixbuf)
        os.chdir(os.path.dirname(self.filename))
        filelist = os.listdir()
        self.filelist = [name for name in filelist if name.split('.')[-1].lower() in self.format_list]
        self.filelist.sort()
        self.image_index = self.filelist.index(self.filename.split('/')[-1])

    def open_dir(self, button):
        dialog = Gtk.FileChooserDialog('Please choose a folder', self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             'Select', Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            os.chdir(dialog.get_filename())
        else:
            dialog.destroy()
            return 0
        dialog.destroy()
        filelist = os.listdir()
        self.filelist = [name for name in filelist if name.split('.')[-1].lower() in self.format_list]
        self.filelist.sort()
        self.image_index = 0
        self.new_image_reset()
        self.filename = self.filelist[0]
        self.load_image()
        if self.auto_orientation:
            self.apply_orientation()
        self.image.set_from_pixbuf(self.pixbuf)

    def save_image(self, button):
        filetype = GdkPixbuf.Pixbuf.get_file_info(self.filename)[0].get_name()
        extension = filetype.replace('e', '')
        filename = 'Gumby.' + extension
        dialog = Gtk.FileChooserDialog('Please write a name for your image', self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name(filename)
        dialog.set_do_overwrite_confirmation(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
        else:
            dialog.destroy()
            return 0
        dialog.destroy()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        image = self.rotated_flipped(pixbuf)
        image.savev(filename, filetype, [], [])

    def on_button_press(self, widget, event, popup):
        if event.button == 3:
            popup.popup(None, None, None, None, 0, event.time)

    def on_resize(self, widget, allocation):
        try:
            if self.win_width != allocation.width or self.win_height != allocation.height:
                self.win_width = allocation.width
                self.win_height = allocation.height
                self.load_image()
                self.pixbuf = self.rotated_flipped(self.pixbuf)
                self.image.set_from_pixbuf(self.pixbuf)
        except:
            pass

    def help_page(self, button):
        dialog = prefs.HelpDialog(self)
        dialog.run()
        dialog.destroy()

    def about_dialog(self, button):
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
        about = Gtk.AboutDialog()
        about.set_program_name('Cheesemaker')
        about.set_version('0.1.5')
        about.set_license(license)
        about.set_wrap_license(True)
        about.set_comments('A simple image viewer.')
        about.set_authors(['David Whitlock <alovedalongthe@gmail.com>'])
        about.set_logo_icon_name('cheesemaker')
        about.run()
        about.destroy()

    def quit_app(self, widget):
        Gtk.main_quit()

def main():
    win = Imagewindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()
