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

from os.path import expanduser, isdir, dirname, abspath
from os import mkdir, sep, path

SSHOT_NAME = 'SSHot'
SSHOT_VERSION = '0.2.0'
SSHOT_AUTHOR = 'Francesco OpenCode Apruzzese <opencode@e-ware.org>'
SSHOT_WEBSITE = 'www.e-ware.org'
SSHOT_PROJECT_WEBSITE = 'http://opencode.github.io/sshot/'

connections_list_columns = ['ID', 'Name', 'Host', 'User',
                            'Password', 'Port', 'Last Connection',
                            'Connections']
user_home = expanduser('~')
base_path = '%s%s%s' % (user_home, sep, '.sshot')
project_path = path.dirname(path.realpath(__file__))

def prepare_environment():

    if not isdir(base_path):
        mkdir(base_path)
    return True
