if __name__ == '__main__':

    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor
    import dbus.glib

    from app import UpnpRapp

    r = UpnpRapp()

    reactor.run()
