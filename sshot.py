import pygtk
pygtk.require('2.0')
import gtk

from datetime import datetime
import sqlite3
from os.path import expanduser

connections_list_columns = ['Name', 'Host', 'Port']
user_home = expanduser('~')


def init_db(conn, cr):

    sql = 'create table if not exists connection (name str, host str, port str)'
    cr.execute(sql)
    conn.commit()


class Sshot:

    def log(self, text):
        print '[%s] %s' % (datetime.today(), text)

    def __init__(self):
        # ----- Init elements
        # ----- DB
        self.log('Open Connection with configuration db')
        conn = sqlite3.connect('%s/%s' % (user_home, 'sshot.db'))
        self.log('Init connection cursor')
        cr = conn.cursor()
        init_db(conn, cr)
        # ----- Window
        self.win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.win.set_title('SSHot')
        self.win_icon = self.win.render_icon(gtk.STOCK_HOME,
                                             gtk.ICON_SIZE_LARGE_TOOLBAR)
        self.win.set_icon(self.win_icon)
        self.win.set_default_size(500, 200)
        self.win.set_position(gtk.WIN_POS_CENTER)
        self.win.connect("delete_event", self.delete_event)
        self.win.connect("destroy", self.destroy)
        self.lbl_connections = gtk.Label('<b>CONNECTIONS</b>')
        self.lbl_connections.set_use_markup(gtk.TRUE)
        self.lst_connections = gtk.ListStore(str, str, str)
        self.trv_connections = gtk.TreeView(model=self.lst_connections)
        for i in range(len(connections_list_columns)):
            # cellrenderer to render the text
            cell = gtk.CellRendererText()
            # the column is created
            col = gtk.TreeViewColumn(connections_list_columns[i],
                                     cell, text=i)
            col.set_resizable(True)
            # and it is appended to the treeview
            self.trv_connections.append_column(col)
        # ----- Content
        self.vbox = gtk.VBox(spacing=10)
        self.hbox_openerp = gtk.HBox(homogeneous=True, spacing=5)
        # ----- Fill content
        self.vbox.pack_start(self.lbl_connections, expand=False)
        self.vbox.pack_start(self.trv_connections)
        self.win.add(self.vbox)
        # ----- Show Window
        self.win.show_all()

        # ----- Extract and show all the connections in the db
        rows = cr.execute('SELECT * FROM connection ORDER BY NAME')
        rows = rows.fetchall()
        self.log('Founded %s records' % str(len(rows)))
        for row in rows:
            self.lst_connections.append(row)

    def main(self):
        gtk.main()

    def destroy(self, widget, data=None):
        return gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        return gtk.FALSE


if __name__ == "__main__":
    sshot = Sshot()
    sshot.main()
