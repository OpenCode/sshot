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
from os import mkdir, sep, path
import subprocess


__NAME__ = 'SSHot'
__VERSION__ = '0.2.0'
__AUTHOR__ = 'Francesco OpenCode Apruzzese <opencode@e-ware.org>'
__WEBSITE__ = 'www.e-ware.org'
__PROJECT_WEBSITE__ = 'http://opencode.github.io/sshot/'

connections_list_columns = ['ID', 'Name', 'Host', 'User',
                            'Password', 'Port', 'Last Connection']
connection_list_field = 'id, name, host, user, password, port, last_connection'
user_home = expanduser('~')
base_path = '%s%s%s' % (user_home, sep, '.sshot')
project_path = path.dirname(path.realpath(__file__))


def log(text):

    print '[%s] %s' % (datetime.today(), text)


def init_db(conn, cr):

    # ----- CREATE TABLE connection IF NOT EXIST
    sql = 'CREATE TABLE IF NOT EXISTS connection'
    sql = '%s (id integer primary key default null, ' % (sql)
    sql = '%sname str, user str, password str, host str, ' % (sql)
    sql = '%sport str, last_connection str)' % (sql)
    cr.execute(sql)
    conn.commit()
    # ----- CREATE TABLE setting IF NOT EXIST
    sql = 'CREATE TABLE IF NOT EXISTS setting'
    sql = '%s (id integer primary key default null, ' % (sql)
    sql = '%skey str, value str)' % (sql)
    cr.execute(sql)
    conn.commit()
    # ----- SET DEFAULT VALUE IN SETTING DB
    #       use_external_terminal
    sql = 'SELECT id FROM setting WHERE key = "use_external_terminal"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES ("use_external_terminal", "False")'
        cr.execute(sql)
        conn.commit()
    #       external_terminal
    sql = 'SELECT id FROM setting WHERE key = "external_terminal"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES ("external_terminal", "")'
        cr.execute(sql)
        conn.commit()
    #       use tray icon
    sql = 'SELECT id FROM setting WHERE key = "use_tray_icon"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES ("use_tray_icon", "True")'
        cr.execute(sql)
        conn.commit()
    return True


def prepare_environment():

    if not isdir(base_path):
        mkdir(base_path)
    return True


class Config():

    conn = False
    cr = False

    FIELDS = {
        'use_external_terminal': ('boolean', False),
        'external_terminal': ('string', ''),
        'use_tray_icon': ('boolean', True),
        }

    use_external_terminal = False
    external_terminal = ''
    use_tray_icon = False

    def get_value(self, key):
        sql = 'SELECT value FROM setting WHERE key = "%s"' % (key)
        res = self.cr.execute(sql)
        res = res.fetchall()
        if not res:
            return self.FIELDS[key][1]
        res = res[0][0]
        # ----- Return a Bool value based on integer value in db
        if self.FIELDS[key][0] == 'boolean':
            if res == 'True':
                return True
            return False
        return res

    def set_value(self, key, value):
        if self.FIELDS[key][0] == 'boolean':
            value = value and 'True' or 'False'
        sql = 'UPDATE setting SET value = "%s" WHERE key = "%s"' % (
            value, key)
        self.cr.execute(sql)
        self.conn.commit()
        return True

    def __init__(self):
        self.conn = sqlite3.connect('%s%s%s' % (base_path,
                                                sep,
                                                'sshot.db'))
        self.cr = self.conn.cursor()


class ConfigForm(QtGui.QMainWindow):

    conn = False
    MainWindow = False

    def _save(self):
        config = Config()
        config.set_value('external_terminal',
                         self.external_terminal.text())
        config.set_value('use_external_terminal',
                         self.use_external_terminal.isChecked())
        config.set_value('use_tray_icon',
                         self.use_tray_icon.isChecked())

    def __init__(self, MainWindow):
        self.MainWindow = MainWindow
        config = Config()
        # ----- Window
        QtGui.QMainWindow.__init__(self)
        self.resize(550, 250)
        self.setWindowTitle('SSHot - Setting Configuration')
        cWidget = QtGui.QWidget(self)

        grid = QtGui.QGridLayout(cWidget)

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
        self.use_tray_icon = QtGui.QCheckBox("")
        self.use_tray_icon.setChecked(
            config.get_value('use_tray_icon'))

        button_save = QtGui.QPushButton('Save')
        button_save.setFont(QtGui.QFont("Times", 10, QtGui.QFont.Bold))
        self.connect(button_save, QtCore.SIGNAL('clicked()'),
                     self._save)

        grid.addWidget(lbl_use_external_terminal, 0, 0)
        grid.addWidget(self.use_external_terminal, 0, 1)
        grid.addWidget(lbl_external_terminal, 1, 0)
        grid.addWidget(self.external_terminal, 1, 1)
        grid.addWidget(lbl_use_tray_icon, 2, 0)
        grid.addWidget(self.use_tray_icon, 2, 1)
        grid.addWidget(button_save, 3, 0)

        cWidget.setLayout(grid)
        self.setCentralWidget(cWidget)

        config = Config()


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
                self, 'Error',
                "Name, Host, User and Password are required",
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
        config = Config()
        if not config.get_value('use_external_terminal'):
            # ----- Create Space to embed terminal
            new_tab = QtGui.QWidget()
            embedWidget = QtGui.QWidget()
            grid = QtGui.QGridLayout(new_tab)
            new_tab.setLayout(grid)
            grid.addWidget(embedWidget, 0, 0)
            embedder_id = str(embedWidget.winId())
            self.tabs.addTab(new_tab, name)
            args = ['xterm', '-title', name, '-into', embedder_id,
                    '-maximized', '-e', 'sshpass', '-p', password,
                    'ssh', complete_host, '-p', port]
        else:
            external_terminal = config.get_value('external_terminal')
            log('Connect using external terminal %s' % (external_terminal))
            complete_command = 'sshpass -p %s ssh %s -p %s' % (
                password, complete_host, port)
            args = [external_terminal, '-e', complete_command]
        subprocess.Popen(args)
        query = 'UPDATE connection SET last_connection = "%s" where id = %s'
        query = query % (datetime.today(), id)
        cr = self.conn.cursor()
        cr.execute(query)
        self.conn.commit()

    def _click_insert(self):
        self.insert_form = InsertForm(self)
        self.insert_form.show()

    def _click_config(self):
        self.config_form = ConfigForm(self)
        self.config_form.show()

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

    def _click_donate(self):
        infos = 'If you like %s (and we are sure you like it!!!) plese considere to donate to the project\n' % (__NAME__)
        infos = '%sOur developer need RedBull to implement new features' % (infos)
        infos = '%s and so we need money to buy RedBull!\n\nHelp us to feed developer\n\n' % (infos)
        infos = '%sPAYPAL: cescoap@gmail.com\n\n' % (infos)
        infos = '%sFLATTR: https://flattr.com/profile/opencode?public=1\n\n' % (infos)
        QtGui.QMessageBox.information(self, 'Info', infos)

    def _click_info(self):
        infos = '%s\n\n' % (__NAME__)
        infos = '%s%s\n\n' % (infos, __PROJECT_WEBSITE__)
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
        # -- Button Quit
        button_quit = QtGui.QAction(QtGui.QIcon("%s/icons/close.png" % (project_path)),
                                    "Quit", self)
        button_quit.setShortcut("Ctrl+Q")
        button_quit.setStatusTip("Exit from application")
        self.connect(button_quit, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('close()'))
        toolbar.addAction(button_quit)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Delete
        button_delete = QtGui.QAction(
            QtGui.QIcon("%s/icons/delete.png" % (project_path)), "Delete", self)
        button_delete.setShortcut("Ctrl+D")
        button_delete.setStatusTip(
            "Delete one or more connections from the table")
        self.connect(button_delete, QtCore.SIGNAL('triggered()'),
                     self._click_delete)
        toolbar.addAction(button_delete)
        # -- Button Insert
        button_insert = QtGui.QAction(
            QtGui.QIcon("%s/icons/add.png" % (project_path)), "Insert", self)
        button_insert.setShortcut("Ctrl+I")
        button_insert.setStatusTip("Insert a new connection")
        self.connect(button_insert, QtCore.SIGNAL('triggered()'),
                     self._click_insert)
        toolbar.addAction(button_insert)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Show Password
        button_show_password = QtGui.QAction(
            QtGui.QIcon("%s/icons/show_password.png" % (project_path)), "Show Password",
            self)
        button_show_password.setShortcut("Ctrl+P")
        button_show_password.setStatusTip(
            "Show password for selected record in the table")
        self.connect(button_show_password, QtCore.SIGNAL('triggered()'),
                     self._click_show_password)
        toolbar.addAction(button_show_password)
        button_refresh = QtGui.QAction(
            QtGui.QIcon("%s/icons/refresh.png" % (project_path)), "Refresh", self)
        button_refresh.setShortcut("F5")
        button_refresh.setStatusTip("Refresh the table to see new information")
        self.connect(button_refresh, QtCore.SIGNAL('triggered()'),
                     self._click_refresh)
        toolbar.addAction(button_refresh)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Config
        button_config = QtGui.QAction(
            QtGui.QIcon("%s/icons/config.png" % (project_path)), "Config", self)
        button_config.setShortcut("Ctrl+S")
        button_config.setStatusTip("Set configuration for the software")
        self.connect(button_config, QtCore.SIGNAL('triggered()'),
                     self._click_config)
        toolbar.addAction(button_config)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Donate
        button_donate = QtGui.QAction(
            QtGui.QIcon("%s/icons/donate.png" % (project_path)), "Info", self)
        button_donate.setShortcut("Ctrl+H")
        button_donate.setStatusTip("Help the poor developer")
        self.connect(button_donate, QtCore.SIGNAL('triggered()'),
                     self._click_donate)
        toolbar.addAction(button_donate)
        # -- Button Info
        button_info = QtGui.QAction(
            QtGui.QIcon("%s/icons/info.png" % (project_path)), "Info", self)
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
        # ------ TrayIcon
        icon = QtGui.QIcon('%s/icons/sshot.png' % (project_path))
        self.systray = QtGui.QSystemTrayIcon(icon)
        menu = QtGui.QMenu()
        ti_show_insert_form = menu.addAction('Insert Connection')
        menu.addSeparator()
        ti_show_action = menu.addAction('Show')
        ti_quit_action = menu.addAction('Quit')
        QtCore.QObject.connect(ti_show_insert_form, QtCore.SIGNAL("triggered()"),
                               self._click_insert)
        QtCore.QObject.connect(ti_quit_action, QtCore.SIGNAL("triggered()"),
                               self.close)
        QtCore.QObject.connect(ti_show_action, QtCore.SIGNAL("triggered()"),
                               self._show_window)
        self.systray.setContextMenu(menu)
        self.systray.show()
        print project_path

    def closeEvent(self,  ev):
        config = Config()
        if config.get_value('use_tray_icon') and self.isVisible():
            self.hide()
            #self.systray.showMessage('SSHot', 'Application in TrayIcon')
            ev.ignore()

    def _show_window(self):
        self.show()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sshot_main = Sshot()
    sshot_main.show()
    sys.exit(app.exec_())
