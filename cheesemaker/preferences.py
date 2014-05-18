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

from PyQt5.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QSpinBox, QCheckBox,
        QGridLayout, QVBoxLayout, QScrollArea)
import os
import configparser

class Config(object):
    """Read, write / create config file."""
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
        slide_delay = int(com['SlideTimeDelay'])
        quality = int(com['Quality'])
        return (orientation, slide_delay, quality)

    def write_config(self, orientation, slide_delay, quality):
        self.config['Common'] = {}
        com = self.config['Common']
        com['AutoOrientation'] = str(orientation)
        com['SlideTimeDelay'] = str(slide_delay)
        com['Quality'] = str(quality)
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

class PrefsDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self.auto_orient = parent.auto_orient
        self.slide_delay = parent.slide_delay
        self.quality = parent.quality

        self.setWindowTitle('Preferences')
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('<b>Automatic orientation</b>'), 0, 0, 1, 2)
        self.orient_check = QCheckBox('Automatic orientation using image data')
        self.orient_check.setChecked(self.auto_orient)
        self.orient_check.toggled.connect(self.orient)
        layout.addWidget(self.orient_check, 1, 0, 1, 2)

        layout.addWidget(QLabel('<b>Slideshow time delay</b>'), 2, 0, 1, 2)
        layout.addWidget(QLabel('Time between images'), 3, 0, 1, 1)
        self.delay_spinb = QSpinBox()
        self.delay_spinb.setRange(1, 50)
        self.delay_spinb.setValue(self.slide_delay)
        layout.addWidget(self.delay_spinb)
        layout.addWidget(self.delay_spinb, 3, 1, 1, 1)

        layout.addWidget(QLabel('<b>Jpeg quality</b>'), 4, 0, 1, 2)
        layout.addWidget(QLabel('Quality of saved Jpeg images'), 5, 0, 1, 1)
        self.qual_spinb = QSpinBox()
        self.qual_spinb.setRange(25, 100)
        self.qual_spinb.setValue(self.quality)
        self.qual_spinb.setSingleStep(5)
        layout.addWidget(self.qual_spinb)
        layout.addWidget(self.qual_spinb, 5, 1, 1, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(200, 250)
        self.show()

    def orient(self):
        self.auto_orient = self.orient_check.isChecked()

class PropsDialog(QDialog):
    """Dialog displaying basic properties of the image."""
    def __init__(self, parent, name, width, height):
        QDialog.__init__(self, parent)

        self.setWindowTitle('Properties')
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('<b>Name</b>'), 0, 0, 1, 1)
        layout.addWidget(QLabel(name), 0, 1, 1, 1)
        layout.addWidget(QLabel('<b>Width</b>'), 1, 0, 1, 1)
        layout.addWidget(QLabel(str(width)), 1, 1, 1, 1)
        layout.addWidget(QLabel('<b>Height</b>'), 2, 0, 1, 1)
        layout.addWidget(QLabel(str(height)), 2, 1, 1, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(200, 100)
        self.show()

class HelpDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self.setWindowTitle('Help!')
        base_dir = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(base_dir, 'data', 'help_page')) as help_file:
            text = help_file.read()

        layout = QVBoxLayout()
        self.setLayout(layout)
        label = QLabel(text)
        label.setWordWrap(True)
        label.setMargin(12)
        scrollwin = QScrollArea()
        scrollwin.setWidget(label)
        layout.addWidget(scrollwin)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.resize(650, 500)
        self.show()
