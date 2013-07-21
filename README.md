# Cheesemaker

A simple image viewer using Python 3 and Gtk 3.

### What's so special about Cheesemaker?

At the moment, Cheesemaker supports zoom, fullscreen, rotating and flipping images, automatic orientation, displaying the images in grayscale, and resizing the image when the window is resized. You can also open images in multiple windows.

There is no menubar or toolbar, but you can access the menu by right-clicking on the window. There are also keyboard shortcuts for most actions. In addition, you can now access some functions by clicking on different parts of the window. For example, if you click near the right edge of the image, it will go to the next image in the folder. The mouse and keyboard shortcuts are all listed in the help page.

There is a slideshow, which can show random images or show the images in order. This option can also be changed while the slideshow is running. The screensaver is disabled while the slideshow is running.

You can save images, but any image (exif) data will be lost.

The preferences (automatic orientation, background color, slideshow time delay, certain save options, and including images in subfolders) are saved for the next time you use Cheesemaker.

### TODO

* Improve saving (add an option to save exif data).
* Put my feet up and relax.
* Try to make it more memory efficient.
* Take it easy for a while.
* Add some edit functions.
* Make it faster.

### Dependencies

Cheesemaker depends on python3, python3-gi and gir1.2-gdkpixbuf-2.0.

### Author

This program has been developed by David Whitlock.
