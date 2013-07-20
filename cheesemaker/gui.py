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

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio
import os, random
from . import preferences
#from . import preferences, editimage

ui_info = """
<ui>
  <popup name='PopupMenu'>
    <menuitem action='Open'/>
    <menuitem action='Opendir'/>
    <separator/>
    <menuitem action='NewWin'/>
    <separator/>
    <menuitem action='Saveas'/>
    <separator/>
    <menu action='EditMenu'>
      <menuitem action='RotateLeft'/>
      <menuitem action='RotateRight'/>
      <separator/>
      <menuitem action='FlipHoriz'/>
      <menuitem action='FlipVert'/>
      <separator/>
      <menuitem action='Desaturate'/>
    </menu>
    <separator/>
    <menu action='ViewMenu'>
      <menuitem action='PrevImg'/>
      <menuitem action='NextImg'/>
      <separator/>
      <menuitem action='ReloadImg'/>
      <separator/>
      <menuitem action='Zoomin'/>
      <menuitem action='Zoomout'/>
      <menuitem action='Zoom1to1'/>
      <menuitem action='Zoomfit'/>
    </menu>
    <menuitem action='Full'/>
    <menuitem action='Slides'/>
    <menu action='SlidesOpts'>
      <menuitem action='NextSlides'/>
      <menuitem action='RandomSlides'/>
    </menu>
    <separator/>
    <menu action='HelpMenu'>
      <menuitem action='Help'/>
      <menuitem action='About'/>
    </menu>
    <separator/>
    <menuitem action='Prefs'/>
    <separator/>
    <menuitem action='CloseWin'/>
    <separator/>
    <menuitem action='Quit'/>
  </popup>
</ui>
"""

class Imagewindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title='Cheesemaker', application=app)

        self.app = app
        self.set_default_size(700, 500)
        self.set_default_icon_name('cheesemaker')
        self.image = Gtk.Image()
        self.img_size = 'Zoomfit'
        self.load_img = self.load_img_fit
        self.win_width = 0
        self.win_height = 0

        self.grid = Gtk.Grid()
        self.add(self.grid)

        action_group = Gtk.ActionGroup('gui_actions')
        self.actions(action_group)
        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)
        self.imageview()

        self.read_preferences()
        self.slideshow_type = 'NextSlides'

        self.popup = uimanager.get_widget('/PopupMenu')
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.STRUCTURE_MASK)
        self.connect('button-press-event', self.on_button_press)

        self.graybutton = uimanager.get_widget('/PopupMenu/EditMenu/Desaturate')
        self.new_img_reset()

        self.readable_list = ['ras', 'tif', 'tiff', 'wmf', 'icns', 'ico', 'png', 'wbmp', 
                'gif', 'pnm', 'tga', 'ani', 'xbm', 'xpm', 'jpg', 'pcx', 'jpeg', 'bmp', 'svg']
        self.writable_list = ['ico', 'png', 'tiff', 'bmp', 'jpeg']

    def actions(self, action_group):
        action_group.add_actions([
            ('Open', Gtk.STOCK_OPEN, '_Open image', None, 'Open image', self.open_image),
            ('Opendir', None, 'Open fol_der', '<Ctrl>D', 'Open folder', self.open_dir),
            ('NewWin', None, 'Open new _window', '<Ctrl><Shift>O', 'Open new window', self.new_win),
            ('Saveas', Gtk.STOCK_SAVE, '_Save image', None, 'Save image', self.save_image),
            ('EditMenu', None, '_Edit'),
            ('RotateLeft', None, 'Rotate _left', '<Ctrl>Left', 'Rotate left', self.img_rotate_left),
            ('RotateRight', None, 'Rotate _right', '<Ctrl>Right', 'Rotate right', self.img_rotate_right),
            ('FlipHoriz', None, 'Flip _horizontally', '<Ctrl>H', 'Flip horizontally', self.img_flip_horiz),
            ('FlipVert', None, 'Flip _vertically', '<Ctrl>V', 'Flip vertically', self.img_flip_vert),
            ('Prefs', None, 'Preferences', '<Ctrl>P', 'Preferences', self.set_preferences),
            ('ViewMenu', None, '_View'),
            ('NextImg', Gtk.STOCK_GO_FORWARD, '_Next image', '<Alt>Right', 'Go to next image', self.go_next_img),
            ('PrevImg', Gtk.STOCK_GO_BACK, '_Previous image', '<Alt>Left', 'Go to previous image', self.go_prev_img),
            ('ReloadImg', Gtk.STOCK_REDO, '_Reload image', '<Ctrl>R', 'Reload image', self.reload_img),
            ('SlidesOpts', None, 'S_lideshow options'),
            ('Zoomin', Gtk.STOCK_ZOOM_IN, 'Zoom in', '<Ctrl>Up', 'Enlarge the image', self.img_zoom_in),
            ('Zoomout', Gtk.STOCK_ZOOM_OUT, 'Zoom out', '<Ctrl>Down', 'Shrink the image', self.img_zoom_out),
            ('HelpMenu', None, '_Help'),
            ('Help', Gtk.STOCK_HELP, 'Help', 'F1', 'Open the help page', self.help_page),
            ('About', Gtk.STOCK_ABOUT, 'About', None, 'About', self.about_dialog),
            ('CloseWin', None, 'Close window', '<Ctrl>W', 'Close window', self.close_win),
            ('Quit', Gtk.STOCK_QUIT, 'Close all windows', None, 'Close all windows', self.quit_app)
            ])

        action_group.add_toggle_actions([
            ('Desaturate', None, 'Toggle _grayscale', None, 'Toggle grayscale', self.toggle_gray),
            ('Full', Gtk.STOCK_FULLSCREEN, '_Fullscreen', 'F11', 'Fullscreen', self.toggle_full),
            ('Slides', None, '_Slideshow', 'F5', 'Slideshow', self.toggle_slides)
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
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        scrolledwindow.connect('size-allocate', self.on_resize)
        self.grid.attach(scrolledwindow, 0, 0, 1, 1)
        scrolledwindow.add_with_viewport(self.image)

    def read_preferences(self):
        try:
            conf = preferences.Config()
            values = conf.read_config()
            self.auto_orientation = values[0]
            self.image.override_background_color(Gtk.StateType.NORMAL, 
                    Gdk.RGBA(values[1][0], values[1][1], values[1][2], values[1][3]))
            self.slide_delay = values[2]
            self.recursive = values[3]
            self.quality = values[4]
            self.rem_exif_data = values[5]
        except:
            self.auto_orientation = True
            self.image.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(0.0, 0.0, 0.0, 1.0))
            self.slide_delay = 5
            self.recursive = False
            self.quality = 90
            self.rem_exif_data = False

    def set_preferences(self, button):
        dialog = preferences.PrefsDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.auto_orientation = dialog.auto_orientation
            self.image.override_background_color(Gtk.StateType.NORMAL, dialog.color_button.get_rgba())
            self.slide_delay = dialog.choose_delay.get_value_as_int()
            self.recursive = dialog.recursive
            self.quality = dialog.choose_quality.get_value_as_int()
            self.rem_exif_data = dialog.rem_exif_data
            conf = preferences.Config()
            conf.write_config(self.auto_orientation, dialog.color_button.get_rgba(), 
                    self.slide_delay, self.recursive, self.quality, self.rem_exif_data)
        dialog.destroy()

    def toggle_slides(self, button):
        if button.get_active():
            self.fullscreen()
            cursor = Gdk.Cursor.new(Gdk.CursorType.BLANK_CURSOR)
            self.get_window().set_cursor(cursor)
            self.slide_cookie = self.app.inhibit(self, Gtk.ApplicationInhibitFlags.IDLE, 'Disable slideshow')
            self.timer_delay = GLib.timeout_add_seconds(self.slide_delay, self.start_slideshow)
        else:
            self.app.uninhibit(self.slide_cookie)
            GLib.source_remove(self.timer_delay)
            self.unfullscreen()
            cursor = Gdk.Cursor.new(Gdk.CursorType.ARROW)
            self.get_window().set_cursor(cursor)

    def start_slideshow(self):
        if self.slideshow_type:
            self.go_next_img(None)
        else:
            self.filename = random.choice(self.filelist)
            self.reload_img(None)
        return True

    def slideshow_options(self, button, current):
        self.slideshow_type = current.get_current_value()

    def toggle_full(self, button):
        if button.get_active():
            self.fullscreen()
        else:
            self.unfullscreen()

    def toggle_gray(self, button):
        if button.get_active():
            self.pixbuf.saturate_and_pixelate(self.pixbuf, 0.0, False)
            self.grays = True
        else:
            self.grays = False
            self.load_img()
            self.pixbuf = self.modified_state()
        self.image.set_from_pixbuf(self.pixbuf)

    def load_img_fit(self):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.win_width, self.win_height)
        self.img_width, self.img_height = self.win_width, self.win_height

    def load_img_1to1(self):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        self.img_width = self.pixbuf.get_width()
        self.img_height = self.pixbuf.get_height()

    def reload_img(self, button):
        self.new_img_reset()
        self.load_img()
        self.set_title(self.filename.rsplit('/', 1)[1])
        if self.auto_orientation:
            self.apply_orientation()
        self.image.set_from_pixbuf(self.pixbuf)

    def apply_orientation(self):
        orient = self.pixbuf.get_option('orientation')
        if orient and orient != '1':
            if orient == '6':
                self.img_rotate_right(None)
            elif orient == '8':
                self.img_rotate_left(None)
            elif orient == '3':
                self.img_rotate_ud()
            elif orient == '2':
                self.img_flip_horiz(None)
            elif orient == '4':
                self.img_flip_vert(None)
            elif orient == '5':
                self.img_rotate_right(None)
                self.img_flip_horiz(None)
            else:
                self.img_rotate_right(None)
                self.img_flip_vert(None)

    def default_zoom_ratio(self, button, current):
        self.img_size = current.get_name()
        if self.img_size == 'Zoomfit':
            self.load_img = self.load_img_fit
        else:
            self.load_img = self.load_img_1to1
        self.load_img()
        self.pixbuf = self.modified_state()
        self.image.set_from_pixbuf(self.pixbuf)

    def img_zoom_in(self, button):
        self.img_zoom(1.25)

    def img_zoom_out(self, button):
        self.img_zoom(0.8)

    def img_zoom(self, zoomratio):
        self.img_width, self.img_height = self.img_width*zoomratio, self.img_height*zoomratio
        self.pixbuf = self.modified_state()
        self.image.set_from_pixbuf(self.pixbuf)

    def go_next_img(self, button):
        self.img_index = self.img_index + 1 if self.img_index < self.last_file else 0
        self.filename = self.filelist[self.img_index]
        self.reload_img(None)

    def go_prev_img(self, button):
        self.img_index = self.img_index - 1 if self.img_index else self.last_file
        self.filename = self.filelist[self.img_index]
        self.reload_img(None)

    def img_rotate_left(self, button):
        self.mod_state = self.mod_state - 1 if self.mod_state else 3
        self.pixbuf = self.modified_state()
        self.image.set_from_pixbuf(self.pixbuf)

    def img_rotate_right(self, button):
        self.mod_state = self.mod_state + 1 if self.mod_state < 3 else 0
        self.pixbuf = self.modified_state()
        self.image.set_from_pixbuf(self.pixbuf)

    def img_rotate_ud(self):
        self.mod_state += 2
        self.mod_state %= 4
        self.pixbuf = self.modified_state()
        self.image.set_from_pixbuf(self.pixbuf)

    def img_flip_horiz(self, button):
        self.pixbuf = self.pixbuf.flip(True)
        self.image.set_from_pixbuf(self.pixbuf)
        self.fliph = not self.fliph

    def img_flip_vert(self, button):
        self.pixbuf = self.pixbuf.flip(False)
        self.image.set_from_pixbuf(self.pixbuf)
        self.flipv = not self.flipv

    def modified_state(self):
        if self.img_size == 'Zoomfit':
            if self.mod_state % 2:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_height, self.img_width)
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.filename, self.img_width, self.img_height)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        if self.mod_state:
            if self.mod_state == 1:
                pixbuf = pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
            elif self.mod_state == 2:
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

    def new_img_reset(self):
        self.mod_state = 0
        self.fliph = False
        self.flipv = False
        self.grays = False
        self.graybutton.set_active(False)

    def open_image(self, button):
        title = 'Please choose a file'
        file_action = Gtk.FileChooserAction.OPEN
        ok_icon = Gtk.STOCK_OPEN
        filefilter = True
        self.filename = self.file_dialog(title, file_action, ok_icon, None, True)
        if not self.filename:
            return
        self.reload_img(None)
        dir_name = os.path.dirname(self.filename)
        if self.recursive:
            self.filelist = [os.path.join(dirname, filename) for dirname, dirnames, filenames 
                    in os.walk(dir_name) for filename in filenames if 
                    filename.rsplit('.', 1)[-1].lower() in self.readable_list]
        else:
            filelist = os.listdir(dir_name)
            self.filelist = [os.path.join(dir_name, name) for name in filelist if 
                    name.rsplit('.', 1)[-1].lower() in self.readable_list]
        self.filelist.sort()
        self.last_file = len(self.filelist) - 1
        self.img_index = self.filelist.index(self.filename)

    def open_dir(self, button):
        title = 'Please choose a folder'
        file_action = Gtk.FileChooserAction.SELECT_FOLDER
        ok_icon = Gtk.STOCK_OPEN
        dir_name = self.file_dialog(title, file_action, ok_icon, None)
        if not dir_name:
            return
        if self.recursive:
            self.filelist = [os.path.join(dirname, filename) for dirname, dirnames, filenames 
                    in os.walk(dir_name) for filename in filenames if 
                    filename.rsplit('.', 1)[-1].lower() in self.readable_list]
        else:
            filelist = os.listdir(dir_name)
            self.filelist = [os.path.join(dir_name, name) for name in filelist if 
                    name.rsplit('.', 1)[-1].lower() in self.readable_list]
        self.filelist.sort()
        self.last_file = len(self.filelist) - 1
        self.img_index = 0
        self.filename = self.filelist[0]
        self.reload_img(None)

    def new_win(self, button):
        self.app.new_win()

    def save_image(self, button):
        filetype = GdkPixbuf.Pixbuf.get_file_info(self.filename)[0].get_name()
        name = self.filename.rsplit('/', 1)[1]
        if filetype in self.writable_list:
            title = 'Please choose a name for your image'
            file_action = Gtk.FileChooserAction.SAVE
            ok_icon = Gtk.STOCK_SAVE
            filename = self.file_dialog(title, file_action, ok_icon, name, False, True)
            if not filename:
                return
        else:
            message = 'Sorry, we cannot save ' + filetype + ' images'
            title = 'Cannot save ' + name
            self.error_dialog(title, message)
            return
        img_size = self.img_size
        self.img_size = 'Zoom1to1'
        pixbuf = self.modified_state()
        option_list, value_list = [], []
        if filetype == 'jpeg':
            option_list.append('quality'); value_list.append(str(self.quality))
        pixbuf.savev(filename, filetype, option_list, value_list)
        self.img_size = img_size

    def file_dialog(self, title, file_action, ok_icon, filename, filefilter=False, saving=False):
        dialog = Gtk.FileChooserDialog(title, self, file_action, 
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             ok_icon, Gtk.ResponseType.OK))
        if filefilter:
            filefilter = Gtk.FileFilter()
            filefilter.add_pixbuf_formats()
            dialog.set_filter(filefilter)
        if saving:
            dialog.set_current_name(filename)
            dialog.set_do_overwrite_confirmation(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = dialog.get_filename()
        else:
            dialog.destroy()
            return
        dialog.destroy()
        return name

    def error_dialog(self, title, message):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                Gtk.ButtonsType.CLOSE, message)
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()

    def on_button_press(self, widget, event):
        if event.button == 1:
            x_pos = event.x_root
            if x_pos < 150:
                if event.state == Gdk.ModifierType.CONTROL_MASK:
                    self.img_rotate_left(None)
                else:
                    self.go_prev_img(None)
            elif x_pos > self.win_width - 150:
                if event.state == Gdk.ModifierType.CONTROL_MASK:
                    self.img_rotate_right(None)
                else:
                    self.go_next_img(None)
        if event.button == 3:
            self.popup.popup(None, None, None, None, 0, event.time)

    def on_resize(self, widget, allocation):
        try:
            if self.win_width != allocation.width or self.win_height != allocation.height:
                self.win_width = allocation.width
                self.win_height = allocation.height
                self.load_img()
                self.pixbuf = self.modified_state()
                self.image.set_from_pixbuf(self.pixbuf)
        except:
            pass

    def help_page(self, button):
        dialog = preferences.HelpDialog(self)
        dialog.run()
        dialog.destroy()

    def about_dialog(self, button):
        dialog = preferences.AboutDialog(self)
        dialog.run()
        dialog.destroy()

    def close_win(self, button):
        self.app.close_win(self)

    def quit_app(self, button):
        self.app.quit()

class Imageapplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self, application_id='org.riverrun.Cheesemaker')
        self.set_flags(Gio.ApplicationFlags.HANDLES_OPEN) # This does not work at the moment

    def do_open(self, files, n_files, hint):
        print(files)
        print(n_files)
        print(hint)

    def do_activate(self):
        win = Imagewindow(self)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def new_win(self):
        win = Imagewindow(self)
        win.show_all()
        self.add_window(win)

    def close_win(self, window):
        if len(self.get_windows()) == 1:
            self.quit()
        else:
            window.destroy()

def main():
    app = Imageapplication()
    app.run(None)
