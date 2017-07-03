from pox.core import core
import pox
import pox.lib.packet as pkt
from pox.lib.revent import *
from pox.openflow.discovery import Discovery
from pox.host_tracker import host_tracker
import pox.openflow.libopenflow_01 as of

class kj_host(EventMixin):
  def __init__ (self):
    def startup ():
      core.openflow.addListeners(self, priority=0)
      core.openflow_discovery.addListeners(self)
      core.host_tracker.addListeners(self)
      """ Here is the place where is created the listener"""
    core.call_when_ready(startup, ('openflow','openflow_discovery', 'host_tracker'))


  def _handle_HostEvent (self, event):
    """ Here is the place where is used the listener"""
    print "Host, switchport and switch...", event.entry
    
  def _handle_PacketIn(self, event):
    """ Packet processing """
def launch():
  from host_tracker import launch
  launch()
  core.registerNew(kj_host)
