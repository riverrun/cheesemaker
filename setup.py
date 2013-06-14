#!/usr/bin/python3
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

import os
from distutils.core import setup

setup(
    name = 'cheesemaker',
    version = '0.1.0',
    packages = ['cheesemaker'],
    scripts = ['bin/cheesemaker'],
    data_files = [
        ('share/applications', ['cheesemaker.desktop']),
        ('share/pixmaps', ['cheesemaker.png']),
        ],
    author = 'David Whitlock',
    author_email = 'alovedalongthe@gmail.com',
    url = 'https://github.com/riverrun/cheesemaker',
    description = 'An image viewer',
    license = 'GPLv3',
)
