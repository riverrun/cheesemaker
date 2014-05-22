Cheesemaker
===========

A minimalistic image viewer using Python3 and Qt5.

Features
~~~~~~~~

At the moment, Cheesemaker supports zoom, fullscreen, rotating and
flipping images, automatic orientation, and resizing and cropping
images. You can also open images in multiple windows.

There is no menubar or toolbar, but you can access the menu by
right-clicking on the window. There are also keyboard shortcuts for most
actions. In addition, you can now access some functions by clicking on
different parts of the window. For example, if you click near the right
edge of the image, it will go to the next image in the folder. The mouse
and keyboard shortcuts are all listed in the help page.

There is a slideshow, which can show random images or show the images in
order. This option can also be changed while the slideshow is running.
The screensaver is disabled while the slideshow is running.

You can save images, and the image (exif) data will be saved. However,
the orientation data will be rewritten, so that the next time you open
the image it will appear the same way.

The preferences (automatic orientation, slideshow time delay and jpeg
image quality) are saved for the next time you use Cheesemaker.

Dependencies
~~~~~~~~~~~~

Cheesemaker depends on python3, python3-pyqt5, python3-pyqt5.qtsvg, qt5-image-formats-plugins,
python3-gobject (python3-gi), and libgexiv2 (gir1.2-gexiv2).

Qt4 version
~~~~~~~~~~~

From version 0.2.5 upto version 0.3.0, this program used PyQt4 (click on
`releases <https://github.com/riverrun/cheesemaker/releases>`_ 
to see the available versions). That version depends
on python3, python3-pyqt4, python3-gobject (python3-gi), and libgexiv2
(gir1.2-gexiv2).

Gtk3 version
~~~~~~~~~~~~

Upto version 0.2.5, this program used Gtk 3 (click on
`releases <https://github.com/riverrun/cheesemaker/releases>`_ 
tab to see the available versions). That version depends on python3,
python3-gobject (python3-gi), gdk-pixbuf2 (gir1.2-gdkpixbuf-2.0) and
libgexiv2 (gir1.2-gexiv2).

TODO
~~~~

-  Make it faster.
-  Put my feet up and relax.
-  Maybe add more basic editing functionality.
-  Maybe improve auto-orientation.
-  Take it easy for a while.

Author
~~~~~~

This program has been developed by David Whitlock.

License
~~~~~~~

Cheesemaker is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.
