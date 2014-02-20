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
from datetime import datetime
import sqlite3
from os.path import expanduser, isdir
from os import mkdir, sep

connections_list_columns = ['ID', 'Name', 'Host', 'Password', 'Port']
connection_list_field = 'id, name, host, password, port'
user_home = expanduser('~')
base_path = '%s%s%s' % (user_home, sep, '.sshot')


def init_db(conn, cr):

    sql = 'create table if not exists connection'
    sql = '%s (id integer primary key default null,' % (sql)
    sql = '%sname str, password str, host str, port str)' % (sql)
    cr.execute(sql)
    conn.commit()
    return True


def prepare_environment():

    if not isdir(base_path):
        mkdir(base_path)
    return True


class Sshot(QtGui.QMainWindow):

    def log(self, text):
        print '[%s] %s' % (datetime.today(), text)

    def __init__(self):
        # ----- Environment
        self.log('Prepare environment...')
        prepare_environment()
        self.log('Environment is ready!')
        # ----- DB
        self.log('Open connection for db')
        conn = sqlite3.connect('%s%s%s' % (base_path,
                                           sep,
                                           'sshot.db'))
        self.log('Init connection cursor')
        cr = conn.cursor()
        init_db(conn, cr)
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(350, 250)
        self.setWindowTitle('SSHot')
        self.statusBar().showMessage('SSHot: A Software To Rule Them All!')
        toolbar = self.addToolBar('Buttons')
        quit = QtGui.QAction(QtGui.QIcon("icons/close.png"), "Quit", self)
        quit.setShortcut("Ctrl+Q")
        quit.setStatusTip("Quit application")
        self.connect(quit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        toolbar.addAction(quit)
        # ----- Extract and show all the connections in the db
        rows = cr.execute('SELECT ' + connection_list_field + ' FROM connection ORDER BY NAME')
        rows = rows.fetchall()
        connections_list = QtGui.QTableWidget(
            len(rows), len(connections_list_columns))
        connections_list.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        # ----- Adapt TableView Columns width to content
        connections_list.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.setCentralWidget(connections_list)
        self.log('Founded %s records' % str(len(rows)))
        # ----- Create header for TableView
        connections_list.setHorizontalHeaderLabels(
            connections_list_columns)
        # ----- Fill TableWidget with db datas
        row_count = 0
        for row in rows:
            for field in range(len(row)):
                item = QtGui.QTableWidgetItem(str(row[field]))
                # ----- The rows are only selectable and not editable
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                connections_list.setItem(row_count, field, item)
            row_count += 1

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sshot_main = Sshot()
    sshot_main.show()
    sys.exit(app.exec_())
