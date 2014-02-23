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


__NAME__ = 'SSHot'
__VERSION__ = '0.1.0'
__AUTHOR__ = 'Francesco OpenCode Apruzzese <opencode@e-ware.org>'
__WEBSITE__ = 'www.e-ware.org'

connections_list_columns = ['ID', 'Name', 'Host', 'User',
                            'Password', 'Port', 'Last Connection']
connection_list_field = 'id, name, host, user, password, port, last_connection'
user_home = expanduser('~')
base_path = '%s%s%s' % (user_home, sep, '.sshot')


def log(text):

    print '[%s] %s' % (datetime.today(), text)


def init_db(conn, cr):

    # ----- CREATE TABLE IF NOT EXIST
    sql = 'CREATE TABLE IF NOT EXISTS connection'
    sql = '%s (id integer primary key default null, ' % (sql)
    sql = '%sname str, user str, password str, host str, ' % (sql)
    sql = '%sport str, last_connection str)' % (sql)
    cr.execute(sql)
    conn.commit()
    return True


def prepare_environment():

    if not isdir(base_path):
        mkdir(base_path)
    return True


class InsertForm(QtGui.QMainWindow):

    conn = False
    MainWindow = False

    def _insert_connection(self):
        name = self.edit_name.text()
        host = self.edit_host.text()
        user = self.edit_user.text()
        password = self.edit_password.text()
        port = self.edit_port.text()
        if not (name and host and user and password):
            QtGui.QMessageBox.warning(
                self, 'Error', "Name, Host, User and Password are required",
                "Continue")
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
            log("Connection %s created!" % (name))
            self.MainWindow.draw_table(cr, self.MainWindow.main_grid)
            self.close()

    def __init__(self, MainWindow):
        self.MainWindow = MainWindow
        self.conn = sqlite3.connect('%s%s%s' % (base_path,
                                                sep,
                                                'sshot.db'))
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(350, 250)
        self.setWindowTitle('SSHot - Insert Connection')
        cWidget = QtGui.QWidget(self)

        grid = QtGui.QGridLayout(cWidget)

        lbl_name = QtGui.QLabel("Name")
        lbl_host = QtGui.QLabel("Host")
        lbl_user = QtGui.QLabel("User")
        lbl_password = QtGui.QLabel("Password")
        lbl_port = QtGui.QLabel("Port")
        self.edit_name = QtGui.QLineEdit()
        self.edit_host = QtGui.QLineEdit()
        self.edit_user = QtGui.QLineEdit()
        self.edit_password = QtGui.QLineEdit()
        self.edit_port = QtGui.QLineEdit()

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


class Sshot(QtGui.QMainWindow):

    connections_list = False
    conn = False
    tabs = False
    main_grid = False

    def _table_double_click(self, clicked_object):
        row = clicked_object.row()
        id = self.connections_list.item(row, 0).text()
        name = self.connections_list.item(row, 1).text()
        host = self.connections_list.item(row, 2).text()
        user = self.connections_list.item(row, 3).text()
        password = self.connections_list.item(row, 4).text()
        port = self.connections_list.item(row, 5).text() or '22'
        log('Connect to %s with user %s' % (host, user))
        complete_host = '%s@%s' % (user, host)
        # ----- Create Space to embed terminal
        new_tab = QtGui.QWidget()
        embedWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout(new_tab)
        new_tab.setLayout(grid)
        grid.addWidget(embedWidget, 0, 0)
        embedder_id = str(embedWidget.winId())
        self.tabs.addTab(new_tab, name)
        args = ['xterm', '-title', name, '-into', embedder_id ,
                '-maximized', '-e', 'sshpass', '-p', password,
                'ssh', complete_host, '-p', port]
        process = subprocess.Popen(args)
        query = 'UPDATE connection SET last_connection = "%s" where id = %s'
        query = query % (datetime.today(), id)
        cr = self.conn.cursor()
        cr.execute(query)
        self.conn.commit()

    def _click_insert(self):
        self.insert_form = InsertForm(self)
        self.insert_form.show()

    def _click_delete(self):
        reply = QtGui.QMessageBox.question(self, 'Delete Records',
                                           "Are you sure?",
                                           QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            select_model = self.connections_list.selectionModel()
            if not select_model.selectedRows():
                QtGui.QMessageBox.warning(
                    self, 'Error',
                    "Select a record from the table to delete it",
                    "Continue")
            else:
                cr = self.conn.cursor()
                query = 'delete from connection where id = %s'
                for model_index in select_model.selectedRows():
                    selected_row = model_index.row()
                    id = self.connections_list.item(selected_row, 0).text()
                    if id:
                        log('Delete connection with id %s' % (id))
                        cr.execute(query % (id))
                        self.conn.commit()
                self.draw_table(cr, self.main_grid)

    def _click_refresh(self):
        cr = self.conn.cursor()
        self.draw_table(cr, self.main_grid)

    def _click_info(self):
        infos = '%s\n' % (__NAME__)
        infos = '%sVersion: %s\n' % (infos, __VERSION__)
        infos = '%sAuthor: %s\n' % (infos, __AUTHOR__)
        infos = '%sWebsite: %s\n' % (infos, __WEBSITE__)
        QtGui.QMessageBox.information(self, 'Info', infos)

    def _click_show_password(self):
        select_model = self.connections_list.selectionModel()
        if not select_model.selectedRows():
            QtGui.QMessageBox.warning(
                self, 'Error',
                "Select a record from the table to read password",
                "Continue")
        else:
            cr = self.conn.cursor()
            query = 'SELECT name, password FROM connection WHERE id = %s'
            passwords = ''
            for model_index in select_model.selectedRows():
                selected_row = model_index.row()
                id = self.connections_list.item(selected_row, 0).text()
                if id:
                    rows = cr.execute(query % (id))
                    rows = rows.fetchall()
                    for row in rows:
                        passwords = '[%s] %s\n%s' % (row[0], row[1],
                                                     passwords)
            if passwords:
                QtGui.QMessageBox.information(self, 'Password',
                                              passwords)

    def draw_table(self, cr, main_grid):
        # ----- Extract and show all the connections in the db
        query = 'SELECT %s FROM connection ORDER BY NAME ASC'
        query = query % (connection_list_field)
        rows = cr.execute(query)
        rows = rows.fetchall()
        # ----- Graphical settings
        connections_list = QtGui.QTableWidget(
            len(rows), len(connections_list_columns))
        main_grid.addWidget(connections_list, 0, 0)
        connections_list.doubleClicked.connect(self._table_double_click)
        connections_list.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        connections_list.hideColumn(0)  # hide id column
        connections_list.hideColumn(4)  # hide id column
        # ----- Adapt TableView Columns width to content
        connections_list.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        #self.setCentralWidget(connections_list)
        log('Founded %s records' % str(len(rows)))
        # ----- Create header for TableView
        connections_list.setHorizontalHeaderLabels(
            connections_list_columns)
        connections_list.horizontalHeader().setClickable(False)
        # ----- Fill TableWidget with db datas
        row_count = 0
        for row in rows:
            for field in range(len(row)):
                item = QtGui.QTableWidgetItem(str(row[field] or ''))
                # ----- The rows are only selectable and not editable
                item.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                connections_list.setItem(row_count, field, item)
            row_count += 1
        # ----- Set generic value
        self.connections_list = connections_list

    def __init__(self):
        # ----- Environment
        log('Prepare environment...')
        prepare_environment()
        log('Environment is ready!')
        # ----- DB
        log('Open connection for db')
        self.conn = sqlite3.connect('%s%s%s' % (base_path,
                                                sep,
                                                'sshot.db'))
        log('Init connection cursor')
        cr = self.conn.cursor()
        init_db(self.conn, cr)
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.resize(900, 600)
        #self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle('SSHot')
        self.statusBar().showMessage('SSHot: A Software To Rule Them All!')
        # ----- Toolbar and relative buttons
        toolbar = self.addToolBar('Buttons')
        button_quit = QtGui.QAction(QtGui.QIcon("icons/close.png"),
                                    "Quit", self)
        button_quit.setShortcut("Ctrl+Q")
        button_quit.setStatusTip("Exit from application")
        self.connect(button_quit, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('close()'))
        toolbar.addAction(button_quit)
        toolbar.addSeparator()
        button_delete = QtGui.QAction(
            QtGui.QIcon("icons/delete.png"), "Delete", self)
        button_delete.setShortcut("Ctrl+D")
        button_delete.setStatusTip("Delete one or more connections from the table")
        self.connect(button_delete, QtCore.SIGNAL('triggered()'),
                     self._click_delete)
        toolbar.addAction(button_delete)
        button_insert = QtGui.QAction(
            QtGui.QIcon("icons/add.png"), "Insert", self)
        button_insert.setShortcut("Ctrl+I")
        button_insert.setStatusTip("Insert a new connection")
        self.connect(button_insert, QtCore.SIGNAL('triggered()'),
                     self._click_insert)
        toolbar.addAction(button_insert)
        toolbar.addSeparator()
        button_show_password = QtGui.QAction(
            QtGui.QIcon("icons/show_password.png"), "Show Password",
            self)
        button_show_password.setShortcut("Ctrl+P")
        button_show_password.setStatusTip("Show password for selected record in the table")
        self.connect(button_show_password, QtCore.SIGNAL('triggered()'),
                     self._click_show_password)
        toolbar.addAction(button_show_password)
        button_refresh = QtGui.QAction(
            QtGui.QIcon("icons/refresh.png"), "Refresh", self)
        button_refresh.setShortcut("F5")
        button_refresh.setStatusTip("Refresh the table to see new information")
        self.connect(button_refresh, QtCore.SIGNAL('triggered()'),
                     self._click_refresh)
        toolbar.addAction(button_refresh)
        toolbar.addSeparator()
        button_info = QtGui.QAction(
            QtGui.QIcon("icons/info.png"), "Info", self)
        button_info.setShortcut("Ctrl+?")
        button_info.setStatusTip("Show information about software")
        self.connect(button_info, QtCore.SIGNAL('triggered()'),
                     self._click_info)
        toolbar.addAction(button_info)
        # ----- Draw the main table
        tabs = QtGui.QTabWidget()
        #tabs.setTabsClosable(True)
        self.tabs = tabs
        main_tab = QtGui.QWidget()
        main_grid = QtGui.QGridLayout(main_tab)
        main_tab.setLayout(main_grid)
        self.main_grid = main_grid
        tabs.addTab(main_tab, 'Connection')
        self.setCentralWidget(tabs)
        self.draw_table(cr, main_grid)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sshot_main = Sshot()
    sshot_main.show()
    sys.exit(app.exec_())
