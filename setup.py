# -*- coding: utf-8 -*-

# Authors: David Whitlock <alovedalongthe@gmail.com>
# A simple image viewer
# Copyright (C) 2013-2014 David Whitlock
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
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

def add_data():
    try:
        data_files = [('share/applications', ['extra/cheesemaker.desktop']),
                ('share/pixmaps', ['extra/cheesemaker.png'])]
        return data_files
    except:
        return

if os.name == 'posix':
    data_files = add_data()
else:
    data_files = None

setup(
    name = 'cheesemaker',
    version = '0.3.8',
    author='David Whitlock',
    author_email='alovedalongthe@gmail.com',
    url = 'https://github.com/riverrun/cheesemaker',
    description = 'A minimalistic image viewer using Python3 and PyQt5',
    long_description=long_description,
    license='GPLv3',
    packages = ['cheesemaker'],
    include_package_data=True,
    data_files=data_files,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Viewers',
    ],
    entry_points={
        'gui_scripts': [
            'cheesemaker = cheesemaker.gui:main',
            ]
        },
)
