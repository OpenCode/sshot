#!/usr/bin/python

# ######################################################################
#
#  SSHot
#
#  Copyright 2014 Francesco OpenCode Apruzzese <opencode@e-ware.org>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ######################################################################

import sys
from PyQt4 import QtGui, QtCore
import sqlite3
from os.path import dirname, abspath
from os import sep

project_abspath = dirname(abspath(__file__))
sys.path.append(project_abspath)
from log import *
from db import *
from environment import *
from config import Config


class ConfigForm(QtGui.QMainWindow):

    conn = False
    MainWindow = False

    def _save(self):
        config = Config(self.conn)
        config.set_value('external_terminal',
                         self.external_terminal.text())
        config.set_value('use_external_terminal',
                         self.use_external_terminal.isChecked())
        config.set_value('use_tray_icon',
                         self.use_tray_icon.isChecked())
        config.set_value('xterm_geometry_columns',
                         self.xterm_geometry_columns.text())
        config.set_value('xterm_geometry_rows',
                         self.xterm_geometry_rows.text())
        config.set_value('xterm_font',
                         self.xterm_font.text())

    def __init__(self, MainWindow):
        self.MainWindow = MainWindow
        self.conn = sqlite3.connect('%s%s%s' % (base_path,
                                                sep,
                                                'sshot.db'))
        config = Config(self.conn)
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(550, 250)
        self.setWindowTitle('SSHot - Setting Configuration')
        cWidget = QtGui.QWidget(self)

        grid = QtGui.QGridLayout(cWidget)

        lbl_application_configuration = QtGui.QLabel(
            "Application Configuration:")
        self.use_tray_icon = QtGui.QCheckBox("")
        self.use_tray_icon.setChecked(
            config.get_value('use_tray_icon'))
        lbl_terminal_configuration = QtGui.QLabel(
            "Terminal Configuration:")
        lbl_xterm_geometry_columns = QtGui.QLabel(
            "Columns")
        self.xterm_geometry_columns = QtGui.QLineEdit(
            str(config.get_value('xterm_geometry_columns')))
        lbl_xterm_geometry_rows = QtGui.QLabel(
            "Rows")
        self.xterm_geometry_rows = QtGui.QLineEdit(
            str(config.get_value('xterm_geometry_rows')))
        lbl_xterm_font = QtGui.QLabel(
            "Font")
        self.xterm_font = QtGui.QLineEdit(
            str(config.get_value('xterm_font')))
        lbl_external_terminal_configuration = QtGui.QLabel(
            "External Terminal Configuration:")
        lbl_use_external_terminal = QtGui.QLabel(
            "Use External Terminal Emulator")
        lbl_external_terminal = QtGui.QLabel("External Emulator")
        lbl_use_tray_icon = QtGui.QLabel(
            "Reduce Application To Try Icon When you close it")
        self.use_external_terminal = QtGui.QCheckBox("")
        self.use_external_terminal.setChecked(
            config.get_value('use_external_terminal'))
        self.external_terminal = QtGui.QLineEdit(
            config.get_value('external_terminal'))

        button_save = QtGui.QPushButton('Save')
        button_save.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.connect(button_save, QtCore.SIGNAL('clicked()'),
                     self._save)

        grid.addWidget(lbl_application_configuration, 0, 0)
        grid.addWidget(lbl_use_tray_icon, 1, 0)
        grid.addWidget(self.use_tray_icon, 1, 1)
        grid.addWidget(lbl_terminal_configuration, 2, 0)
        grid.addWidget(lbl_xterm_geometry_columns, 3, 0)
        grid.addWidget(self.xterm_geometry_columns, 3, 1)
        grid.addWidget(lbl_xterm_geometry_rows, 4, 0)
        grid.addWidget(self.xterm_geometry_rows, 4, 1)
        grid.addWidget(lbl_xterm_font, 5, 0)
        grid.addWidget(self.xterm_font, 5, 1)
        grid.addWidget(lbl_external_terminal_configuration, 6, 0)
        grid.addWidget(lbl_use_external_terminal, 7, 0)
        grid.addWidget(self.use_external_terminal, 7, 1)
        grid.addWidget(lbl_external_terminal, 8, 0)
        grid.addWidget(self.external_terminal, 8, 1)
        grid.addWidget(button_save, 9, 0)

        cWidget.setLayout(grid)
        self.setCentralWidget(cWidget)
