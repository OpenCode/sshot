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
import subprocess

connections_list_columns = ['ID', 'Name', 'Host', 'User',
                            'Password', 'Port']
connection_list_field = 'id, name, host, user, password, port'
user_home = expanduser('~')
base_path = '%s%s%s' % (user_home, sep, '.sshot')


def init_db(conn, cr):

    sql = 'create table if not exists connection'
    sql = '%s (id integer primary key default null,' % (sql)
    sql = '%sname str, user str, password str, host str, port str)' % (sql)
    cr.execute(sql)
    conn.commit()
    return True


def prepare_environment():

    if not isdir(base_path):
        mkdir(base_path)
    return True


class InsertForm(QtGui.QMainWindow):

    def _insert_connection(self):
        print 'Du Sumfing, plz!!!'

    def __init__(self):
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(350, 250)
        self.setWindowTitle('SSHot - Insert Connection')
        cWidget = QtGui.QWidget(self)

        grid = QtGui.QGridLayout(cWidget)

        edit_name = QtGui.QLineEdit("Name")
        edit_host = QtGui.QLineEdit("Host")
        edit_user = QtGui.QLineEdit("User")
        edit_password = QtGui.QLineEdit("Passowrd")
        edit_port = QtGui.QLineEdit("Port")

        button_save = QtGui.QPushButton('Save');
        button_save.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold));
        self.connect(button_save, QtCore.SIGNAL('clicked()'),
                     self._insert_connection);

        grid.addWidget(edit_name, 0, 0)
        grid.addWidget(edit_host, 0, 1)
        grid.addWidget(edit_user, 1, 0)
        grid.addWidget(edit_password, 1, 1)
        grid.addWidget(edit_port, 2, 0)
        grid.addWidget(button_save, 2, 1)

        cWidget.setLayout(grid)
        self.setCentralWidget(cWidget)


class Sshot(QtGui.QMainWindow):

    connections_list = False
    conn = False

    def log(self, text):
        print '[%s] %s' % (datetime.today(), text)

    def _table_double_click(self, clicked_object):
        row = clicked_object.row()
        host = self.connections_list.item(row, 2).text()
        user = self.connections_list.item(row, 3).text()
        password = self.connections_list.item(row, 4).text()
        port = self.connections_list.item(row, 5).text()
        port = port or '22'
        self.log('Connect to %s with user %s' % (host, user))
        complete_host = '%s@%s' % (user, host)
        args = ['xterm', '-e', 'sshpass', '-p', password,
                'ssh', complete_host, '-p', port]
        subprocess.Popen(args)

    def _click_insert(self):
        self.insert_form = InsertForm()
        self.insert_form.show()

    def _click_delete(self):
        select_model = self.connections_list.selectionModel()
        if not select_model.selectedRows():
            QtGui.QMessageBox.warning(
                self, 'Error', "Select a record from the table to delete it",
                "Continue")
        cr = self.conn.cursor()
        query = 'delete from connection where id = %s'
        for model_index in select_model.selectedRows():
            selected_row = model_index.row()
            id = self.connections_list.item(selected_row, 0).text()
            if id:
                self.log('Delete connection with id %s' % (id))
                cr.execute(query % (id))
                self.conn.commit()
        self.draw_table(cr)

    def draw_table(self, cr):
        # ----- Extract and show all the connections in the db
        rows = cr.execute('SELECT ' + connection_list_field + ' FROM connection ORDER BY NAME')
        rows = rows.fetchall()
        connections_list = QtGui.QTableWidget(
            len(rows), len(connections_list_columns))
        connections_list.doubleClicked.connect(self._table_double_click)
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
        # ----- Set generic value
        self.connections_list = connections_list

    def __init__(self):
        # ----- Environment
        self.log('Prepare environment...')
        prepare_environment()
        self.log('Environment is ready!')
        # ----- DB
        self.log('Open connection for db')
        self.conn = sqlite3.connect('%s%s%s' % (base_path,
                                                sep,
                                                'sshot.db'))
        self.log('Init connection cursor')
        cr = self.conn.cursor()
        init_db(self.conn, cr)
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(350, 250)
        self.setWindowTitle('SSHot')
        self.statusBar().showMessage('SSHot: A Software To Rule Them All!')
        # ----- Toolbar and relative buttons
        toolbar = self.addToolBar('Buttons')
        button_quit = QtGui.QAction(QtGui.QIcon("icons/close.png"),
                                    "Quit", self)
        button_quit.setShortcut("Ctrl+Q")
        button_quit.setStatusTip("Quit application")
        self.connect(button_quit, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('close()'))
        toolbar.addAction(button_quit)
        button_delete = QtGui.QAction(
            QtGui.QIcon("icons/delete.png"), "Delete", self)
        button_delete.setShortcut("Ctrl+D")
        button_delete.setStatusTip("Delete Connection")
        self.connect(button_delete, QtCore.SIGNAL('triggered()'),
                     self._click_delete)
        toolbar.addAction(button_delete)
        button_insert = QtGui.QAction(
            QtGui.QIcon("icons/add.png"), "Insert", self)
        button_insert.setShortcut("Ctrl+I")
        button_insert.setStatusTip("Insert Connection")
        self.connect(button_insert, QtCore.SIGNAL('triggered()'),
                     self._click_insert)
        toolbar.addAction(button_insert)
        # ----- Draw the main table
        self.draw_table(cr)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sshot_main = Sshot()
    sshot_main.show()
    sys.exit(app.exec_())
