from pox.core import core
import pox.openflow.libopenflow_01 as of
import networkx as nx

from networkx.algorithms.shortest_paths.generic import shortest_path
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr

log = core.getLogger()

def build_topology_graph():
    g = nx.Graph()
    nodes = {l_i.dpid1 for l_i in core.openflow_discovery.adjacency.keys()}
    g.add_nodes_from(nodes)
    for link in core.openflow_discovery.adjacency.keys():
        g.add_edge(link.dpid1, link.dpid2)
    return g

def find_path(nx_graph, src_dpid, target_dpid):
    return shortest_path(nx_graph, src_dpid, target_dpid)

def get_link_ports(src_dpid, target_dpid):
    links = list(core.openflow_discovery.adjacency.keys())
    log.debug("Links: %s", links)
    link = [l_i for l_i in links
            if l_i.dpid1 == src_dpid
            and l_i.dpid2 == target_dpid]
    if len(link) == 0:
        return None

    return link[0].port1, link[0].port2

def get_ingress_port(path, dpid):
    hop_number = path.index(dpid)
    if hop_number == 0:
        return 1 # The default host port

    local_port, remote_port = \
            get_link_ports(path[hop_number - 1], path[hop_number])
    return remote_port

# a UDP OpenFlow match
def build_udp_match( source_mac
                   , destination_mac
                   , source_ip
                   , destination_ip
                   , source_port
                   , destination_port
                   , in_port):
    the_match = of.ofp_match()
    the_match.in_port = in_port
    the_match.dl_src = EthAddr(source_mac)
    the_match.dl_dst = EthAddr(destination_mac)
    the_match.dl_type = 0x0800
    the_match.nw_src = IPAddr(source_ip)
    the_match.nw_dst = IPAddr(destination_ip)
    the_match.nw_proto = 17
    the_match.tp_src = source_port
    the_match.tp_dst = destination_port
    return the_match

# Create a flowmod that matches on packets
def build_flow_rule(match, output_port):
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.actions.append(of.ofp_action_output(port=output_port))
    msg.priority = 65534
    return msg

# Install a flow rule on a switch
def install_flow_rule(flowmod, dpid):
    core.l2_learning.switch_connections[dpid].send(flowmod)

# host entry attached to a switch
def get_host_info(dpid):
    host = [e for e in core.host_tracker.entryByMAC.values()
            if e.dpid == dpid]
    if len(host) == 0:
        raise ValueError("Couldn't find host entry (pingall before start)")
    host = host[0]

    return {
        "ip": str(next(iter(host.ipAddrs.keys()))),
        "mac": str(host.macaddr),
        "port": host.port
    }

def install_path_rules(path,
                          final_dpid,
                          src,
                          dst,
                          source_port,
                          destination_port):
    for idx, switch in enumerate(path):
        switch = path[idx]

        in_port = get_ingress_port(path, switch)

        # Determine output port
        if switch == path[-1]:
            out_port = get_host_info(final_dpid)["port"]
        else:
            next_hop = path[idx + 1]
            out_port = get_link_ports(switch, next_hop)[0]

        match = build_udp_match(
            src["mac"],
            dst["mac"],
            src["ip"],
            dst["ip"],
            source_port,
            destination_port,
            in_port
        )

        rule = build_flow_rule(match, out_port)
        install_flow_rule(rule, switch)

        log.info("[FLOW] dpid=%s in=%s out=%s",
                    switch, in_port, out_port)
            
def install_middlebox_flow(src_dpid,
                               dst_dpid,
                               mb_dpid,
                               source_port,
                               destination_port):

    graph = build_topology_graph()

    # Resolve host info
    src = get_host_info(src_dpid)
    dst = get_host_info(dst_dpid)

    log.info("[SETUP] src=%s (%s) -> dst=%s (%s)",
             src["ip"], src["mac"], dst["ip"], dst["mac"])
    log.info("[SETUP] middlebox switch=%s", mb_dpid)


    # client to middlebox
    client_path = find_path(
        graph, src_dpid, mb_dpid
    )
    log.info("[PATH] client -> middlebox: %s", client_path)

    install_path_rules(
        client_path,
        mb_dpid,
        src,
        dst,
        source_port,
        destination_port
    )


    # middlebox to server
    server_path = find_path(
        graph, mb_dpid, dst_dpid
    )
    log.info("[PATH] middlebox -> server: %s", server_path)

    install_path_rules(
        server_path,
        dst_dpid,
        src,
        dst,
        source_port,
        destination_port
    )

def do_install():
    src_dpid = None
    dst_dpid = None
    mb_dpid = None
    source_port = None
    destination_port = None
    install_middlebox_flow(src_dpid, dst_dpid, mb_dpid,
            source_port, destination_port)
