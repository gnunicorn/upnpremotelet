if __name__ == '__main__':

    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    import dbus.glib

    from twisted.internet import reactor
    from twisted.internet import task

    from coherence.base import Coherence
    from coherence.upnp.devices.control_point import ControlPoint

    coherence = Coherence({'logmode':'warning'})
    ctp = ControlPoint(coherence, auto_client=['MediaRenderer'])

    from rendering_client import MediaRendererClient
    client = MediaRendererClient(coherence)

    from icon import StatusIconController
    icon = StatusIconController()

    def observe():
        print client.__dict__

    #uid = sys.argv[0]
    def found_one(device=None, udn=None):
        if not device:
            device = coherence.get_device_with_id(udn)

        print "connecting to %s" % device.get_friendly_name()
        client.connect(device)
        icon.connect(client)

        from mmkeys import Mmkeys
        keyer = Mmkeys(client)

    #reactor.callLater(0.2, client.connect, uid)
    ctp.connect(found_one, 'Coherence.UPnP.ControlPoint.MediaRenderer.detected')
    #task.LoopingCall(observe).start(1.0)
    reactor.run()
