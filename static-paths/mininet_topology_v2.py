#!/usr/bin/python

from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel

class PartBTopo(Topo):

    def __init__(self):
        "Create Topology"
        Topo.__init__(self)

        # Add hosts
        host_a = self.addHost('host_a')
        host_b   = self.addHost('host_b')
        host_c = self.addHost('host_c')

        # Add switches (acting as L3 routers, no controller)
        r1 = self.addSwitch('r1', listenPort=6634)
        r2 = self.addSwitch('r2', listenPort=6635)
        r3 = self.addSwitch('r3', listenPort=6636)

        # Host-to-switch links
        self.addLink(host_a, r1) 
        self.addLink(host_b,   r2) 
        self.addLink(host_c, r3) 

        # Switch-to-switch links
        self.addLink(r1, r2) 
        self.addLink(r1, r3) 
        self.addLink(r2, r3) 

def run():
    "Create and configure network"
    topo = PartBTopo()
    net = Mininet(topo=topo, link=TCLink, controller=None)

    host_a = net.get('host_a')
    host_a.intf('host_a-eth0').setIP('10.1.1.17', 24)
    host_a.intf('host_a-eth0').setMAC('aa:aa:aa:aa:aa:aa')

    host_b = net.get('host_b')
    host_b.intf('host_b-eth0').setIP('10.4.4.48', 24)
    host_b.intf('host_b-eth0').setMAC('b0:b0:b0:b0:b0:b0')

    host_c = net.get('host_c')
    host_c.intf('host_c-eth0').setIP('10.6.6.69', 24)
    host_c.intf('host_c-eth0').setMAC('cc:cc:cc:cc:cc:cc')

    r1 = net.get('r1')
    r1.intf('r1-eth1').setMAC('00:00:00:01:01:01')  
    r1.intf('r1-eth2').setMAC('00:00:00:01:01:02')  
    r1.intf('r1-eth3').setMAC('00:00:00:01:01:03')  

    r2 = net.get('r2')
    r2.intf('r2-eth1').setMAC('00:00:00:02:02:01')  
    r2.intf('r2-eth2').setMAC('00:00:00:02:02:02')  
    r2.intf('r2-eth3').setMAC('00:00:00:02:02:03')  

    r3 = net.get('r3')
    r3.intf('r3-eth1').setMAC('00:00:00:03:03:01')  
    r3.intf('r3-eth2').setMAC('00:00:00:03:03:02')  
    r3.intf('r3-eth3').setMAC('00:00:00:03:03:03')  

    net.start()

    host_a.cmd('route add default gw 10.1.1.14 dev host_a-eth0')
    host_b.cmd('route add default gw 10.4.4.14 dev host_b-eth0')
    host_c.cmd('route add default gw 10.6.6.46 dev host_c-eth0')

    host_a.cmd('arp -s 10.1.1.14 00:00:00:01:01:01 -i host_a-eth0')
    host_b.cmd('arp -s 10.4.4.14 00:00:00:02:02:01 -i host_b-eth0')
    host_c.cmd('arp -s 10.6.6.46 00:00:00:03:03:01 -i host_c-eth0')

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
