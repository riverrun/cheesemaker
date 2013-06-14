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
# along with cheesemaker.  If not, see <http://www.gnu.org/licenses/gpl.html>.

from gi.repository import Gtk, Gdk, GdkPixbuf
import os

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
    </menu>
    <menu action='ViewMenu'>
      <menuitem action='Nextimg'/>
      <menuitem action='Previmg'/>
      <separator/>
      <menuitem action='ShowMenuBar'/>
      <menuitem action='ShowToolBar'/>
      <separator/>
      <menuitem action='Full'/>
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
        Gtk.Window.__init__(self, title='cheesemaker')

        self.set_default_size(700, 500)
        #self.set_default_icon_name('cheesemaker')
        self.image = Gtk.Image()
        self.image_size = 'Zoomfit'

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

        popup = uimanager.get_widget('/PopupMenu')
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK|Gdk.EventMask.STRUCTURE_MASK)
        self.connect('button_press_event', self.on_button_press, popup)

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
            ('ViewMenu', None, '_View'),
            ('Nextimg', Gtk.STOCK_GO_FORWARD, '_Next image', '<Alt>Right', 'Next image', self.go_next_image),
            ('Previmg', Gtk.STOCK_GO_BACK, '_Previous image', '<Alt>Left', 'Previous image', self.go_prev_image),
            ('ZoomMenu', None, '_Zoom'),
            ('Zoomin', Gtk.STOCK_ZOOM_IN, 'Zoom in', '<Ctrl>Up', 'Zoom in', self.image_zoom_in),
            ('Zoomout', Gtk.STOCK_ZOOM_OUT, 'Zoom out', '<Ctrl>Down', 'Zoom out', self.image_zoom_out),
            ('HelpMenu', None, '_Help'),
            ('Help', Gtk.STOCK_HELP, 'Help', 'F1', 'Open the help page in your web browser', self.help_page),
            ('About', Gtk.STOCK_ABOUT, 'About', None, 'About', self.about_dialog),
            ('Quit', Gtk.STOCK_QUIT, 'Quit', None, 'Quit', self.quit_app)
            ])

        action_group.add_toggle_actions([
            ('Desaturate', None, 'Toggle _grayscale', None, 'Toggle grayscale', self.toggle_gray),
            ('Full', Gtk.STOCK_FULLSCREEN, 'Fullscreen', 'F11', 'Fullscreen', self.toggle_full),
            ('ShowMenuBar', None, 'Show _menubar', None, 'Show menubar', self.toggle_menu, True),
            ('ShowToolBar', None, 'Show _toolbar', None, 'Show toolbar', self.toggle_tool, True)
            ])

        action_group.add_radio_actions([
            ('Zoom1to1', Gtk.STOCK_ZOOM_100, 'Original size', '<Ctrl>0', 'Original size', 1),
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
        self.grid.attach(self.scrolledwindow, 0, 2, 1, 1)
        self.scrolledwindow.add_with_viewport(self.image)

    def toggle_full(self, button):
        if button.get_active():
            self.fullscreen()
        else:
            self.unfullscreen()

    def toggle_menu(self, button):
        if button.get_active():
            self.menubar.show()
        else:
            self.menubar.hide()

    def toggle_tool(self, button):
        if button.get_active():
            self.toolbar.show()
        else:
            self.toolbar.hide()

    def toggle_gray(self, button):
        if button.get_active():
            self.pixbuf.saturate_and_pixelate(self.pixbuf, 0.0, False)
            self.grays = True
            self.image.set_from_pixbuf(self.pixbuf)
        else:
            self.load_image()
            self.grays = False

    def new_image_reset(self):
        self.rotate_state = 0
        self.fliph = False
        self.flipv = False
        self.grays = False
        for name in self.graylist:
            name.set_active(False)

    def default_zoom_ratio(self, button, current):
        self.image_size = current.get_name()
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        self.pixbuf = self.rotated_flipped(pixbuf)
        if self.image_size == 'Zoomfit':
            self.load_image_fit()
        else:
            self.load_image_1to1()

    def load_image(self):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        if self.image_size == 'Zoomfit':
            self.load_image_fit()
        else:
            self.load_image_1to1()
        self.new_image_reset()

    def load_image_fit(self):
        allocation = self.scrolledwindow.get_allocation()
        self.width = allocation.width
        self.height = allocation.height
        ratio = self.width/self.height
        image_width = self.pixbuf.get_width()
        image_height = self.pixbuf.get_height()
        image_ratio = image_width/image_height
        if ratio > image_ratio:
            self.width = min(self.height*image_ratio, image_width)
        else:
            self.height = min(self.width/image_ratio, image_height)
        self.pixbuf = self.pixbuf.scale_simple(self.width, self.height, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(self.pixbuf)

    def load_image_1to1(self):
        self.width = self.pixbuf.get_width()
        self.height = self.pixbuf.get_height()
        self.image.set_from_pixbuf(self.pixbuf)

    def image_zoom_in(self, button):
        self.image_zoom(1.25)

    def image_zoom_out(self, button):
        self.image_zoom(0.8)

    def image_zoom(self, zoomratio):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        self.pixbuf = self.rotated_flipped(pixbuf)
        self.width, self.height = self.width*zoomratio, self.height*zoomratio
        self.pixbuf = self.pixbuf.scale_simple(self.width, self.height, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(self.pixbuf)

    def go_next_image(self, button):
        if self.image_index < len(self.filelist)-1:
            self.image_index += 1
        else:
            self.image_index = 0
        self.filename = self.filelist[self.image_index]
        self.load_image()

    def go_prev_image(self, button):
        if self.image_index > 0:
            self.image_index -= 1
        else:
            self.image_index = len(self.filelist)-1
        self.filename = self.filelist[self.image_index]
        self.load_image()

    def image_rotate_left(self, button):
        self.pixbuf = self.pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE)
        self.image.set_from_pixbuf(self.pixbuf)
        if self.rotate_state > 0:
            self.rotate_state -= 1
        else:
            self.rotate_state = 3

    def image_rotate_right(self, button):
        self.pixbuf = self.pixbuf.rotate_simple(GdkPixbuf.PixbufRotation.CLOCKWISE)
        self.image.set_from_pixbuf(self.pixbuf)
        if self.rotate_state < 3:
            self.rotate_state += 1
        else:
            self.rotate_state = 0

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
        self.load_image()
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
        self.filename = self.filelist[0]
        self.load_image()

    def save_image(self, button):
        dialog = Gtk.FileChooserDialog('Please write a name for your image', self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name('Gumby')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = dialog.get_filename()
        else:
            dialog.destroy()
            return 0
        dialog.destroy()
        filetype = GdkPixbuf.Pixbuf.get_file_info(self.filename)[0].get_name()
        image_size = GdkPixbuf.Pixbuf.get_file_info(self.filename)[1:]
        self.width, self.height = image_size[0], image_size[1]
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.filename)
        image = self.rotated_flipped(pixbuf)
        extension = filetype.replace('e', '')
        filename = name + '.' + extension
        image.savev(filename, filetype, [], [])

    def on_button_press(self, widget, event, popup):
        if event.button == 3:
            popup.popup(None, None, None, None, 0, event.time)

    def help_page(self, button):
        pass

    def about_dialog(self, button):
        about = Gtk.AboutDialog()
        about.set_program_name('cheesemaker')
        about.set_version('0.1.0')
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_comments('An image viewer')
        about.set_authors(['David Whitlock <alovedalongthe@gmail.com>'])
        about.run()
        about.destroy()

    def quit_app(self, widget):
        Gtk.main_quit()

def main():
    win = Imagewindow()
    win.connect('delete-event', Gtk.main_quit)
    win.show_all()
    Gtk.main()