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
from os.path import dirname, abspath
from os import sep
import subprocess

project_abspath = dirname(abspath(__file__))
sys.path.append(project_abspath)
sys.path.append('%s%s%s' % (project_abspath, sep, 'utils'))
sys.path.append('%s%s%s' % (project_abspath, sep, 'forms'))
from log import *
from db import *
from environment import *
from config import Config
from config_form import ConfigForm
from insert_form import InsertForm


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
        config = Config(self.conn)
        if not config.get_value('use_external_terminal'):
            # ----- Create Space to embed terminal
            new_tab = QtGui.QWidget()
            #embedWidget = QtGui.QWidget()
            embedWidget = QtGui.QX11EmbedWidget()
            grid = QtGui.QGridLayout(new_tab)
            new_tab.setLayout(grid)
            grid.addWidget(embedWidget, 0, 0)
            embedder_id = str(embedWidget.winId())
            self.tabs.addTab(new_tab, name)
            complete_command = 'sshpass -p %s ssh %s -p %s; bash' % (
                password, complete_host, port)
            args = ['xterm', '-title', name, '-into', embedder_id,
                    '-font', config.get_value('xterm_font'),
                    '-geometry', '140x30',
                    '-maximized', '-e', complete_command]
        else:
            external_terminal = config.get_value('external_terminal')
            log('Connect using external terminal %s' % (external_terminal))
            complete_command = 'sshpass -p %s ssh %s -p %s' % (
                password, complete_host, port)
            args = [external_terminal, '-e', complete_command]
        subprocess.Popen(args)
        cr = self.conn.cursor()
        query = 'UPDATE connection SET last_connection = "%s" where id = %s'
        query = query % (datetime.today(), id)
        cr.execute(query)
        # ----- Save connection in history
        query = "INSERT INTO history (connection_id, date) VALUES (%s, '%s')"
        query = query % (id, datetime.today())
        cr.execute(query)
        self.conn.commit()

    def _close_tab(self, tab_index):
        if tab_index:
            current_tab = self.tabs.widget(tab_index)
            for widget_child in current_tab.findChildren(QtGui.QWidget):
                widget_child.destroy(destroySubWindows=True)
            self.tabs.removeTab(tab_index)

    def _click_insert(self):
        self.insert_form = InsertForm(self)
        self.insert_form.show()

    def _click_edit(self):
        select_model = self.connections_list.selectionModel()
        if not select_model.selectedRows():
            QtGui.QMessageBox.warning(
                self, 'Error',
                "Select a record from the table to modify it",
                "Continue")
        else:
            model_index = select_model.selectedRows()[0]
            selected_row = model_index.row()
            id = self.connections_list.item(selected_row, 0).text()
            self.insert_form = InsertForm(self, record_id=id)
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
        infos = '''
        If you like %s (and we are sure you like it!!!)
        please considere to donate to the project

        Our developer need RedBull to implement new features
        and so we need money to buy RedBull!

        Help us to feed developer

        PAYPAL: cescoap@gmail.com
        FLATTR: https://flattr.com/profile/opencode?public=1
        ''' % (SSHOT_NAME)
        QtGui.QMessageBox.information(self, 'Info', infos)

    def _click_info(self):
        infos = '%s\n\n' % (SSHOT_NAME)
        infos = '%s%s\n\n' % (infos, SSHOT_PROJECT_WEBSITE)
        infos = '%sVersion: %s\n' % (infos, SSHOT_VERSION)
        infos = '%sAuthor: %s\n' % (infos, SSHOT_AUTHOR)
        infos = '%sWebsite: %s\n' % (infos, SSHOT_WEBSITE)
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
        connections_list.hideColumn(4)  # hide password column
        # ----- Adapt TableView Columns width to content
        connections_list.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        log('Founded %s records' % str(len(rows)))
        # ----- Create header for TableView
        connections_list.setHorizontalHeaderLabels(
            connections_list_columns)
        connections_list.horizontalHeader().setClickable(False)
        # ----- Fill TableWidget with db datas
        row_count = 0
        for row in rows:
            # ----- Add connections count in row
            query = 'SELECT COUNT(id) FROM history WHERE connection_id = %s'
            query = query % (row[0])
            connection_rows = cr.execute(query).fetchall()
            row = row + (str(connection_rows[0][0]), )
            # ----- Filling
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
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.setWindowTitle('SSHot')
        self.statusBar().showMessage(
            'SSHot: A Software To Rule Them All!')
        # ----- Toolbar and relative buttons
        toolbar = self.addToolBar('Buttons')
        # -- Button Quit
        button_quit = QtGui.QAction(
            QtGui.QIcon("%s/icons/close.png" % (project_path)),
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
            QtGui.QIcon("%s/icons/delete.png" % (project_path)),
            "Delete", self)
        button_delete.setShortcut("Ctrl+D")
        button_delete.setStatusTip(
            "Delete one or more connections from the table")
        self.connect(button_delete, QtCore.SIGNAL('triggered()'),
                     self._click_delete)
        toolbar.addAction(button_delete)
        # -- Button Insert
        button_insert = QtGui.QAction(
            QtGui.QIcon("%s/icons/add.png" % (project_path)),
            "Insert", self)
        button_insert.setShortcut("Ctrl+I")
        button_insert.setStatusTip("Insert a new connection")
        self.connect(button_insert, QtCore.SIGNAL('triggered()'),
                     self._click_insert)
        toolbar.addAction(button_insert)
        # -- Button Edit
        button_edit = QtGui.QAction(
            QtGui.QIcon("%s/icons/edit.png" % (project_path)),
            "Edit", self)
        button_edit.setShortcut("Ctrl+E")
        button_edit.setStatusTip("Modify connection")
        self.connect(button_edit, QtCore.SIGNAL('triggered()'),
                     self._click_edit)
        toolbar.addAction(button_edit)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Show Password
        button_show_password = QtGui.QAction(
            QtGui.QIcon("%s/icons/show_password.png" % (project_path)),
            "Show Password", self)
        button_show_password.setShortcut("Ctrl+P")
        button_show_password.setStatusTip(
            "Show password for selected record in the table")
        self.connect(button_show_password, QtCore.SIGNAL('triggered()'),
                     self._click_show_password)
        toolbar.addAction(button_show_password)
        button_refresh = QtGui.QAction(
            QtGui.QIcon("%s/icons/refresh.png" % (project_path)),
            "Refresh", self)
        button_refresh.setShortcut("F5")
        button_refresh.setStatusTip(
            "Refresh the table to see new information")
        self.connect(button_refresh, QtCore.SIGNAL('triggered()'),
                     self._click_refresh)
        toolbar.addAction(button_refresh)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Config
        button_config = QtGui.QAction(
            QtGui.QIcon("%s/icons/config.png" % (project_path)),
            "Config", self)
        button_config.setShortcut("Ctrl+S")
        button_config.setStatusTip("Set configuration for the software")
        self.connect(button_config, QtCore.SIGNAL('triggered()'),
                     self._click_config)
        toolbar.addAction(button_config)
        # -- Separator
        toolbar.addSeparator()
        # -- Button Donate
        button_donate = QtGui.QAction(
            QtGui.QIcon("%s/icons/donate.png" % (project_path)),
            "Info", self)
        button_donate.setShortcut("Ctrl+H")
        button_donate.setStatusTip("Help the poor developer")
        self.connect(button_donate, QtCore.SIGNAL('triggered()'),
                     self._click_donate)
        toolbar.addAction(button_donate)
        # -- Button Info
        button_info = QtGui.QAction(
            QtGui.QIcon("%s/icons/info.png" % (project_path)),
            "Info", self)
        button_info.setShortcut("Ctrl+?")
        button_info.setStatusTip("Show information about software")
        self.connect(button_info, QtCore.SIGNAL('triggered()'),
                     self._click_info)
        toolbar.addAction(button_info)
        # ----- Content creation
        tabs = QtGui.QTabWidget()
        tabs.setTabsClosable(True)
        QtCore.QObject.connect(tabs,
                               QtCore.SIGNAL('tabCloseRequested(int)'),
                               self._close_tab)
        self.tabs = tabs
        main_tab = QtGui.QWidget()
        main_grid = QtGui.QGridLayout(main_tab)
        main_tab.setLayout(main_grid)
        self.main_grid = main_grid
        tabs.addTab(main_tab, 'Connection')
        self.setCentralWidget(tabs)
        # ----- Draw the main table
        self.draw_table(cr, main_grid)
        # ------ TrayIcon
        icon = QtGui.QIcon('%s/icons/sshot.png' % (project_path))
        self.systray = QtGui.QSystemTrayIcon(icon)
        menu = QtGui.QMenu()
        ti_show_insert_form = menu.addAction('Insert Connection')
        menu.addSeparator()
        ti_show_action = menu.addAction('Show')
        ti_quit_action = menu.addAction('Quit')
        QtCore.QObject.connect(ti_show_insert_form,
                               QtCore.SIGNAL("triggered()"),
                               self._click_insert)
        QtCore.QObject.connect(ti_quit_action,
                               QtCore.SIGNAL("triggered()"),
                               self.close)
        QtCore.QObject.connect(ti_show_action,
                               QtCore.SIGNAL("triggered()"),
                               self._show_window)
        self.systray.setContextMenu(menu)
        self.systray.show()

    def closeEvent(self,  ev):
        config = Config(self.conn)
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
