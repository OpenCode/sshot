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

    def __init__(self, conn):
        self.conn = conn
        self.cr = self.conn.cursor()
