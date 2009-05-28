

from coherence.base import Coherence
from coherence.upnp.devices.control_point import ControlPoint

from icon import StatusIconController
from mmkeys import MMKeysController
from rendering_client import MediaRendererClient

import gconf


gconf_keys = {
    'udn': '/apps/mupnp/udn',
    'autoconnect': '/apps/mupnp/autoconnect',
    'mmkeys': '/apps/mupnp/mmkeys',
}


class UpnpRapp(object):

    def __init__(self):
        self.gconf = gconf.client_get_default()
        self.coherence = Coherence({'logmode':'warning'})
        self.ctp = ControlPoint(self.coherence,
                auto_client=['MediaRenderer'])

        self.client = MediaRendererClient(self.coherence)

        self.gui = StatusIconController(self)
        self.gui.connect(self.client)

        self.mmkeys = MMKeysController(name='MUPnPApp')
        # hack to make it start
        if True or self.gconf.get_bool(gconf_keys['mmkeys']) is True:
            self.mmkeys.connect(self.client)


        self.ctp.connect(self._renderer_found,
                'Coherence.UPnP.ControlPoint.MediaRenderer.detected')

        self.ctp.connect(self._renderer_removed,
                'Coherence.UPnP.ControlPoint.MediaRenderer.removed')

    def _renderer_found(self, device=None, udn=None):
        # FIXME: take care about the auto connect if not connected yet
        # instead of just connecting
        if not device:
            device = self.coherence.get_device_with_id(udn)

        print "connecting to %s" % device.get_friendly_name()
        self.connect(device)

    def _renderer_removed(self, device=None, uid=None):
        pass

    def set_autoconnect(self, value):
        self.gconf.set_boolean(gconf_keys['autoconnect'], value)

    def set_multimediakeys(self, value):
        self.gconf.set_boolean(gconf_keys['mmkeys'], value)
        self._load_mmkeys = value

        # reloading
        if not value:
            self.mmkeys.disconnect()
        else:
            self.mmkeys.connect(self.client)

    def connect(self, device):
        #self.gconf.set_string(gconf_keys['udn'], device)

        self.client.disconnect()
        self.client.connect(device)
        # HACK!
        self.gui._connection_state_changed(True)

