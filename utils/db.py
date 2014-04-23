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

connection_list_field = 'id, name, host, user, password, port, last_connection'


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
    # ----- CREATE TABLE history IF NOT EXIST
    sql = 'CREATE TABLE IF NOT EXISTS history'
    sql = '%s (id integer primary key default null, ' % (sql)
    sql = '%sconnection_id integer, date str)' % (sql)
    cr.execute(sql)
    conn.commit()
    # ----- SET DEFAULT VALUE IN SETTING DB
    #       use_external_terminal
    sql = 'SELECT id FROM setting WHERE key = "use_external_terminal"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES \
              ("use_external_terminal", "False")'
        cr.execute(sql)
        conn.commit()
    #       external_terminal
    sql = 'SELECT id FROM setting WHERE key = "external_terminal"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES \
              ("external_terminal", "")'
        cr.execute(sql)
        conn.commit()
    #       use tray icon
    sql = 'SELECT id FROM setting WHERE key = "use_tray_icon"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES \
              ("use_tray_icon", "True")'
        cr.execute(sql)
        conn.commit()
    #       xterm geometry - columns number
    sql = 'SELECT id FROM setting WHERE key = "xterm_geometry_columns"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES \
              ("xterm_geometry_columns", "140")'
        cr.execute(sql)
        conn.commit()
    #       xterm geometry - rows number
    sql = 'SELECT id FROM setting WHERE key = "xterm_geometry_rows"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES \
              ("xterm_geometry_rows", "30")'
        cr.execute(sql)
        conn.commit()
    #       xterm font
    sql = 'SELECT id FROM setting WHERE key = "xterm_font"'
    res = cr.execute(sql)
    if not res.fetchall():
        sql = 'INSERT INTO setting (key, value) VALUES \
              ("xterm_font", "-*-fixed-medium-r-*-*-18-*-*-*-*-*-iso8859-*")'
        cr.execute(sql)
        conn.commit()
    return True
