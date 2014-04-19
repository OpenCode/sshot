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


class InsertForm(QtGui.QMainWindow):

    conn = False
    MainWindow = False
    record_id = False

    def _insert_connection(self):
        record_id = self.record_id
        name = self.edit_name.text()
        host = self.edit_host.text()
        user = self.edit_user.text()
        password = self.edit_password.text()
        port = self.edit_port.text()
        # ----- Check if all the fields are filled
        if not (name and host and user and password):
            QtGui.QMessageBox.warning(
                self, 'Error',
                "Name, Host, User and Password are required",
                "Continue")
        else:
            # ----- Update or Create record for ssh connection
            if record_id:
                query = 'UPDATE connection SET '
                query = "%sname='%s'," % (query, name)
                query = "%shost='%s'," % (query, host)
                query = "%suser='%s'," % (query, user)
                query = "%spassword='%s'," % (query, password)
                query = "%sport='%s'" % (query, port)
                query = "%s WHERE id = %s" % (query, record_id)
            else:
                query = 'INSERT INTO connection (%s) VALUES ('
                query = query % (connection_list_field.replace('id, ', ''))
                query = "%s'%s'," % (query, name)
                query = "%s'%s'," % (query, host)
                query = "%s'%s'," % (query, user)
                query = "%s'%s'," % (query, password)
                query = "%s'%s'," % (query, port)
                query = "%s'')" % query
            cr = self.conn.cursor()
            cr.execute(query)
            self.conn.commit()
            log("Connection %s %s!" % (name,
                                       record_id and 'updated' or 'created'))
            self.MainWindow.draw_table(cr, self.MainWindow.main_grid)
            self.close()

    def __init__(self, MainWindow, record_id=False):
        self.MainWindow = MainWindow
        self.record_id = record_id
        self.conn = sqlite3.connect('%s%s%s' % (base_path,
                                                sep,
                                                'sshot.db'))
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(350, 250)
        self.setWindowTitle('SSHot - Insert Connection')
        cWidget = QtGui.QWidget(self)

        grid = QtGui.QGridLayout(cWidget)

        # ----- Read data to autofill existing fields
        if record_id:
            query = 'SELECT name,host,user,password,port FROM connection \
                     WHERE id = %s' % (record_id)
            rows = self.conn.execute(query)
            rows = rows.fetchall()

        lbl_id = QtGui.QLabel("ID")
        lbl_name = QtGui.QLabel("Name")
        lbl_host = QtGui.QLabel("Host")
        lbl_user = QtGui.QLabel("User")
        lbl_password = QtGui.QLabel("Password")
        lbl_port = QtGui.QLabel("Port")
        self.edit_id = QtGui.QLineEdit(record_id and str(record_id) or '')
        self.edit_name = QtGui.QLineEdit(record_id and str(rows[0][0]) or '')
        self.edit_host = QtGui.QLineEdit(record_id and str(rows[0][1]) or '')
        self.edit_user = QtGui.QLineEdit(record_id and str(rows[0][2]) or '')
        self.edit_password = QtGui.QLineEdit(
            record_id and str(rows[0][3]) or '')
        self.edit_port = QtGui.QLineEdit(record_id and str(rows[0][4]) or '')

        button_save = QtGui.QPushButton('Save')
        button_save.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.connect(button_save, QtCore.SIGNAL('clicked()'),
                     self._insert_connection)

        grid.addWidget(lbl_name, 0, 0)
        grid.addWidget(self.edit_name, 0, 1)
        grid.addWidget(lbl_host, 1, 0)
        grid.addWidget(self.edit_host, 1, 1)
        grid.addWidget(lbl_user, 2, 0)
        grid.addWidget(self.edit_user, 2, 1)
        grid.addWidget(lbl_password, 3, 0)
        grid.addWidget(self.edit_password, 3, 1)
        grid.addWidget(lbl_port, 4, 0)
        grid.addWidget(self.edit_port, 4, 1)
        grid.addWidget(button_save, 5, 0)

        cWidget.setLayout(grid)
        self.setCentralWidget(cWidget)
