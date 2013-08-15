# Cheesemaker

A simple image viewer using Python 3 and Gtk 3.

### What's so special about Cheesemaker?

At the moment, Cheesemaker supports zoom, fullscreen, rotating and flipping images, automatic orientation, displaying the images in grayscale, and resizing and cropping images. You can also open images in multiple windows.

There is no menubar or toolbar, but you can access the menu by right-clicking on the window. There are also keyboard shortcuts for most actions. In addition, you can now access some functions by clicking on different parts of the window. For example, if you click near the right edge of the image, it will go to the next image in the folder. The mouse and keyboard shortcuts are all listed in the help page.

There is a slideshow, which can show random images or show the images in order. This option can also be changed while the slideshow is running. The screensaver is disabled while the slideshow is running.

You can save images, and the image (exif) data will be saved. However, the orientation data will be rewritten, so that the next time you open the image it will appear the same way.

The preferences (automatic orientation, background color, slideshow time delay, jpeg image quality, and including images in subfolders) are saved for the next time you use Cheesemaker.

### TODO

* Put my feet up and relax.
* Maybe add more basic editing functionality.
* Take it easy for a while.
* Make it faster.

### Dependencies

Cheesemaker depends on python3, python3-gobject (python3-gi), gdk-pixbuf2 (gir1.2-gdkpixbuf-2.0) and libgexiv2 (gir1.2-gexiv2).

### Author

This program has been developed by David Whitlock.
