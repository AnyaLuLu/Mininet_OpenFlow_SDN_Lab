#!/usr/bin/env bash

for switch in r1 r2 r3; do
    ovs-vsctl set bridge $switch protocols=OpenFlow13
done

for switch in r1 r2 r3; do
    protos=$(ovs-vsctl get bridge $switch protocols)
    echo "Switch $switch supports $protos"
done

ofctl='ovs-ofctl -O OpenFlow13'


$ofctl add-flow r1 \
    ip,nw_src=10.1.1.17,nw_dst=10.4.4.48,actions=mod_dl_src:00:00:00:01:01:02,mod_dl_dst:00:00:00:02:02:02,output=2

$ofctl add-flow r2 \
    ip,nw_src=10.1.1.17,nw_dst=10.4.4.48,actions=mod_dl_src:00:00:00:02:02:01,mod_dl_dst:b0:b0:b0:b0:b0:b0,output=1


$ofctl add-flow r2 \
    ip,nw_src=10.4.4.48,nw_dst=10.1.1.17,actions=mod_dl_src:00:00:00:02:02:02,mod_dl_dst:00:00:00:01:01:02,output=2

$ofctl add-flow r1 \
    ip,nw_src=10.4.4.48,nw_dst=10.1.1.17,actions=mod_dl_src:00:00:00:01:01:01,mod_dl_dst:aa:aa:aa:aa:aa:aa,output=1


$ofctl add-flow r2 \
    ip,nw_src=10.4.4.48,nw_dst=10.6.6.69,actions=mod_dl_src:00:00:00:02:02:03,mod_dl_dst:00:00:00:03:03:03,output=3

$ofctl add-flow r3 \
    ip,nw_src=10.4.4.48,nw_dst=10.6.6.69,actions=mod_dl_src:00:00:00:03:03:01,mod_dl_dst:cc:cc:cc:cc:cc:cc,output=1


$ofctl add-flow r3 \
    ip,nw_src=10.6.6.69,nw_dst=10.4.4.48,actions=mod_dl_src:00:00:00:03:03:03,mod_dl_dst:00:00:00:02:02:03,output=3

$ofctl add-flow r2 \
    ip,nw_src=10.6.6.69,nw_dst=10.4.4.48,actions=mod_dl_src:00:00:00:02:02:01,mod_dl_dst:b0:b0:b0:b0:b0:b0,output=1

for switch in r1 r2 r3; do
    echo "Flows installed in $switch:"
    $ofctl dump-flows $switch
    echo ""
done
