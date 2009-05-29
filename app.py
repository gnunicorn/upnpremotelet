

from coherence.base import Coherence
from coherence.upnp.devices.control_point import ControlPoint

from icon import StatusIconController
from mmkeys import MMKeysController
from rendering_client import MediaRendererClient

import gconf


gconf_keys = {
    'uuid': '/apps/mupnp/uuid',
    'autoconnect': '/apps/mupnp/autoconnect',
    'mmkeys': '/apps/mupnp/mmkeys',
}


class UpnpRapp(object):

    def __init__(self):

        # configuration setup
        self.gconf = gconf.client_get_default()
        self.conf = {
            'autoconnect': self.gconf.get_bool(gconf_keys['autoconnect']),
            'uuid': self.gconf.get_string(gconf_keys['uuid']),
            'mmkeys': self.gconf.get_bool(gconf_keys['mmkeys']),
        }

        # coherence setup
        self.coherence = Coherence({'logmode':'warning'})
        self.ctp = ControlPoint(self.coherence,
                auto_client=['MediaRenderer'])

        # internals setup
        self.client = MediaRendererClient(self.coherence)

        self.gui = StatusIconController(self)
        self.gui.connect(self.client)

        self.mmkeys = MMKeysController(name='MUPnPApp')
        # hack to make it start
        if True or self.conf['mmkeys'] is True:
            self.mmkeys.connect(self.client)

        # signal connection
        self.ctp.connect(self._renderer_found,
                'Coherence.UPnP.ControlPoint.MediaRenderer.detected')

        self.ctp.connect(self._renderer_removed,
                'Coherence.UPnP.ControlPoint.MediaRenderer.removed')

    def _renderer_found(self, device=None, udn=None):
        # FIXME: take care about the auto connect if not connected yet
        # instead of just connecting
        if not device:
            device = self.coherence.get_device_with_id(udn)

        self.gui._new_renderer(device, udn)
        if not self.client.device and self.conf['autoconnect']:
            if device.uuid == self.uuid:
                self.connect(device, udn)

    def _renderer_removed(self, device=None, uid=None):
        return
        self.gui._renderer_removed(device, uid)

    def set_autoconnect(self, value):
        self.conf['autoconnect'] = value
        self.gconf.set_bool(gconf_keys['autoconnect'], value)

    def set_mmkeys(self, value):
        self.conf['mmkeys'] = value
        self.gconf.set_bool(gconf_keys['mmkeys'], value)
        # reloading
        if not value:
            self.mmkeys.disconnect()
        else:
            self.mmkeys.connect(self.client)

    def connect(self, device):
        print "connecting to %s" % device.get_friendly_name()
        self.gconf.set_string(gconf_keys['uuid'], str(device.uuid))

        self.client.disconnect()
        self.client.connect(device)
        # HACK!
        self.gui._connection_state_changed(True)
