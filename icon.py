
import gtk
import pygtk
pygtk.require('2.0')

import time

class StatusIconController(object):

    def __init__(self, app):
        self.app = app
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_stock(gtk.STOCK_ABOUT)
        self.status_icon.connect('popup-menu', self.show_options)
        self.status_icon.connect('activate', self.show_menu)

        self.playing = False

        self._menu_setup()
        self._options_menu_setup()
        self.disconnect()
        self.status_icon.set_visible(True)

    def connect(self, controller):
        assert self.controller is None
        assert controller
        self.controller = controller

    def disconnect(self):
        self.controller = None

    def show_menu(self, widget):
        # FIXME: what is the time-value to make it show up?
        self.menu.show_all()
        self.menu.popup(None, None, None, 3, int(time.time()))

    def show_options(self, widget, button, time):
        self.opt_menu.show_all()
        self.opt_menu.popup(None, None, None, 3, time)

    def _connection_state_changed(self, state):
        self._sensitive_menu(state)

    def _sensitive_menu(self, val):
        self.item_play.set_sensitive(val)
        self.item_stop.set_sensitive(val)
        self.item_next.set_sensitive(val)
        self.item_prev.set_sensitive(val)

    def _set_playing_status(self, playing):
        if playing != self.playing:
            img = gtk.Image()
            img.set_from_stock(gtk.STOCK_MEDIA_PAUSE if playing \
                    else gtk.STOCK_MEDIA_PLAY, gtk.ICON_SIZE_MENU)
            self.item_play.set_image(img)
            self.playing = playing

    def _toggle_playing(self, widget):
        self._wrapped(widget, 'pause' if self.playing else 'play')

    def _wrapped(self, widget, method):
        getattr(self.controller, method)()

    def _autoconnect_toggle(self, widget):
        self.app.set_autoconnect(widget.get_active())

    def _mmkeys_toggle(self, widget):
        self.app.set_mmkeys(widget.get_active())

    def _menu_setup(self):
        self.menu = gtk.Menu()
        self.item_play = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
        self.item_play.connect('activate', self._toggle_playing)
        self.item_stop = gtk.ImageMenuItem(gtk.STOCK_MEDIA_STOP)
        self.item_stop.connect('activate', self._wrapped, 'stop')
        self.item_next = gtk.ImageMenuItem(gtk.STOCK_MEDIA_NEXT)
        self.item_next.connect('activate', self._wrapped, 'next')
        self.item_prev = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PREVIOUS)
        self.item_prev.connect('activate', self._wrapped, 'previous')

        self.menu.append(self.item_stop)
        self.menu.append(self.item_prev)
        self.menu.append(self.item_next)
        self.menu.append(self.item_play)

    def _options_menu_setup(self):
        self.opt_menu = gtk.Menu()

        autoconnect_item = gtk.CheckMenuItem('Autoconnect')
        autoconnect_item.set_active(self.app.conf['autoconnect'])
        autoconnect_item.connect('toggled', self._autoconnect_toggle)

        mmkeys_item = gtk.CheckMenuItem('Multimedia keys')
        mmkeys_item.set_active(self.app.conf['mmkeys'])
        mmkeys_item.connect('toggled', self._mmkeys_toggle)

        self.devices_menu = gtk.Menu()
        players_item = gtk.MenuItem("select player")
        players_item.set_submenu(self.devices_menu)

        self.opt_menu.append(autoconnect_item)
        self.opt_menu.append(mmkeys_item)
        self.opt_menu.append(players_item)


if __name__ == '__main__':
    st = StatusIconController()
    gtk.main()
