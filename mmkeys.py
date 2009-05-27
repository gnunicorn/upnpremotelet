# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# Copyright 2009 - Benjamin Kampmann <ben.kampmann@googlemail.com>


import dbus

from logging import getLogger
log = getLogger('mmkeys')

class Mmkeys(object):

    def __init__(self, controller, name="Mmmmkey"):
        self.name = name
        self.controller = controller
        self.bus = dbus.SessionBus()

        self.bus_object = self.bus.get_object('org.gnome.SettingsDaemon',
                '/org/gnome/SettingsDaemon/MediaKeys')

        self.bus_object.connect_to_signal("MediaPlayerKeyPressed",
                self._key_pressed,
                dbus_interface='org.gnome.SettingsDaemon.MediaKeys')
        self.iface = dbus.Interface(self.bus_object,
                'org.gnome.SettingsDaemon.MediaKeys')
        self.iface.GrabMediaPlayerKeys(self.name, 0)

    def stop(self):
        self.iface.ReleaseMediaPlayerKeys(self.name)

    def _key_pressed(self, application, key):
        log.debug("received: %s, %s" % (application, key))
        if application != self.name:
            # not for us
            return

        lower_key = key.lower() # we have lowercase thingies
        log.debug("processing: %s" % lower_key)

        try:
            getattr(self.controller, lower_key, None)()
        except AttributeError:
            log.info("%r -> %s does not exist" % (self.controller, lower_key))
        except Exception, e:
            log.warn("%r -> %s failed: %r" % (self.controller, lower_key, e))


if __name__ == '__main__':
    import dbus.glib
    class DummyController(object):
        def __init__(self, methods=[]):
            for m in methods:
                setattr(self, m, self._printer(m))

        def _printer(self, name):
            def wrapped():
                print name
            return wrapped

    ctl = DummyController(['play', 'pause', 'previous', 'next'])
    mm = Mmkeys(ctl)
    import gobject
    gobject.MainLoop().run()

