
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.util import str_to_bool
from pox.lib.packet.arp import arp

import time
from pox.lib.addresses import IPAddr 
from pox.lib.addresses import EthAddr 
from pox.host_tracker import kj_global
log = core.getLogger()

_flood_delay = 0

class LearningSwitch (object):
  def __init__ (self, connection, transparent):
    self.connection = connection
    self.transparent = transparent

    self.macToPort = {}

    connection.addListeners(self)

    self.hold_down_expired = _flood_delay == 0


  def _handle_PacketIn (self, event):

    packet = event.parsed
    #log.info("**Inside handle_packet inside l2_earning*** %s", packet.dst)
    def flood (message = None):
      """ Floods the packet """
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        # Only flood if we've been connected for a little while...

        if self.hold_down_expired is False:
          # Oh yes it is!
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
        # OFPP_FLOOD is optional; on some switches you may need to change
        # this to OFPP_ALL.
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass
        #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    def drop (duration = None):
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    self.macToPort[packet.src] = event.port # 1

    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return

    if packet.dst.is_multicast:
      flood() # 3a
    else:
      if packet.dst not in self.macToPort: # 4
	
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: # 5
          # 5a
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop(10)
          return
        # 6
	log.info("hostsDown %s",kj_global.hostsDown['ip'])
	tof=isinstance(packet.find("arp"),type(None))
	#log.info("p,dst ip:%s %s",str(packet.dst),type(packet.find("arp").protosrc))
	#type(packet.find("arp").protosrc) == class 'pox.lib.addresses.IPAddr'	
	temp=0
	temp2=0
	if tof == False :
     	#log.debug("%s ARP request %s => %s", dpid_to_str(dpid),a.protosrc, a.protodst)
		tof=isinstance(packet.find("arp").protosrc,type(None))
		if tof == False:
			log.info("p,dst ip:%s %s > %s",str(packet.dst),str(packet.find("arp").protosrc), str(packet.find("arp").protodst))
			#kj_global.hostsDown['ip']=str(packet.find("arp").protosrc)
			if str(packet.find("arp").protodst) in kj_global.hostsDown['ip']:
				if str(packet.find("arp").protosrc) =="10.0.0.1":
	         			packet.dst=EthAddr("fe:24:e2:fa:39:56")
		 			log.info("inside link break")
					tem2=1
		 			msg = of.ofp_flow_mod()
		 			#msg.actions.append(of.ofp_action_nw_addr.set_dst(IPAddr(kj_global.hostsDown['ip'])))
		 			#msg.actions.append(of.ofp_action_nw_addr.set_dst(EthAddr('0e:40:cd:09:bb:89')))
		 			#msg.actions.append(of.ofp_action_output(port = 5))
					temp=1
          				msg.match = of.ofp_match.from_packet(packet, event.port)
          				msg.idle_timeout = 10
          				msg.hard_timeout = 30
          				msg.actions.append(of.ofp_action_output(port = port))
          				msg.data = event.ofp # 6a
          				self.connection.send(msg)
	if temp == 0 :	
	  	log.info("checking execution****inside packet.dst  not in self.macToPort %s",packet.dst)# added by jose
          	log.debug("installing flow for %s.%i -> %s.%i" %
                  	(packet.src, event.port, packet.dst, port))
          	msg = of.ofp_flow_mod()
          	msg.match = of.ofp_match.from_packet(packet, event.port)
          	msg.idle_timeout = 10
          	msg.hard_timeout = 30
          	msg.actions.append(of.ofp_action_output(port = port))
          	msg.data = event.ofp # 6a
          	self.connection.send(msg)


class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent):
    core.openflow.addListeners(self)
    self.transparent = transparent

  def _handle_ConnectionUp (self, event):
    log.debug("Connection %s" % (event.connection,))
    if( event.dpid == 2 ):
		log.info("Click triggered")
    else :
    		LearningSwitch(event.connection, self.transparent)

#testing


  def _handle_ConnectionDown (self, event):
    log.debug("Connection down %s" % (event.connection,))
    LearningSwitch(event.connection, self.transparent)


#testing ends


def launch (transparent=False, hold_down=_flood_delay):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  core.registerNew(l2_learning, str_to_bool(transparent))
