

from coherence.base import Coherence
from coherence.upnp.devices.control_point import ControlPoint

from upnpremotelet.status_icon_controller import StatusIconController
from upnpremotelet.mmkeys_controller import MMKeysController
from upnpremotelet.media_renderer_client import MediaRendererClient

import gconf
import sys


gconf_keys = {
    'udn': '/apps/mupnp/udn',
    'autoconnect': '/apps/mupnp/autoconnect',
    'mmkeys': '/apps/mupnp/mmkeys',
}


class UpnpRapp(object):

    def __init__(self):

        # configuration setup
        self.gconf = gconf.client_get_default()
        self.conf = {
            'autoconnect': self.gconf.get_bool(gconf_keys['autoconnect']),
            'udn': self.gconf.get_string(gconf_keys['udn']),
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
        if True or self.conf['mmkeys']:
            self.mmkeys.connect(self.client)

        # signal connection
        self.ctp.connect(self._renderer_found,
                'Coherence.UPnP.ControlPoint.MediaRenderer.detected')

        self.ctp.connect(self._renderer_removed,
                'Coherence.UPnP.ControlPoint.MediaRenderer.removed')

    def _renderer_found(self, device=None, udn=None, client=None):
        # FIXME: take care about the auto connect if not connected yet
        # instead of just connecting
        if not device:
            device = self.coherence.get_device_with_id(udn)

        self.gui.device_found(device, udn)
        if not self.client.device and self.conf['autoconnect']:
            if device.udn == self.conf['udn']:
                self.connect(device)

    def _renderer_removed(self, device=None, udn=None):
        return
        self.gui.renderer_removed(device, udn)

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

    def quit(self, value=0):
        # FIXME: we should disconnect and stuff here
        sys.exit(value)

    def connect(self, device):
        print "connecting to %s" % device.get_friendly_name()
        self.gconf.set_string(gconf_keys['udn'], str(device.udn))

        self.client.disconnect()
        self.client.connect(device)
        # HACK!
        self.gui._connection_state_changed(True, device)

