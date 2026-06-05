#!/usr/bin/env bash

for switch in s1 s2 s3 s4 s6; do
    ovs-vsctl set bridge $switch protocols=OpenFlow13
done

for switch in s1 s2 s3 s4 s6; do
    protos=$(ovs-vsctl get bridge $switch protocols)
    echo "Switch $switch supports $protos"
done

ofctl="ovs-ofctl -O OpenFlow13"



# h1 -> h4
$ofctl add-flow s1 in_port=1,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0a:00:01:02:00:00,mod_dl_dst:0a:00:04:02:00:00,output=3
$ofctl add-flow s2 in_port=3,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0a:00:01:02:00:00,mod_dl_dst:0a:00:04:02:00:00,output=4
$ofctl add-flow s3 in_port=2,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0a:00:01:02:00:00,mod_dl_dst:0a:00:04:02:00:00,output=3
$ofctl add-flow s4 in_port=2,ip,nw_src=10.0.1.2,nw_dst=10.0.4.2,actions=mod_dl_src:0a:00:01:02:00:00,mod_dl_dst:0a:00:04:02:00:00,output=1

# h4 -> h1
$ofctl add-flow s4 in_port=1,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0a:00:04:02:00:00,mod_dl_dst:0a:00:01:02:00:00,output=2
$ofctl add-flow s3 in_port=3,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0a:00:04:02:00:00,mod_dl_dst:0a:00:01:02:00:00,output=2
$ofctl add-flow s2 in_port=4,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0a:00:04:02:00:00,mod_dl_dst:0a:00:01:02:00:00,output=3
$ofctl add-flow s1 in_port=3,ip,nw_src=10.0.4.2,nw_dst=10.0.1.2,actions=mod_dl_src:0a:00:04:02:00:00,mod_dl_dst:0a:00:01:02:00:00,output=1



# h1 -> h2
$ofctl add-flow s1 in_port=1,ip,nw_src=10.0.1.2,nw_dst=10.0.2.2,actions=mod_dl_src:0a:00:01:02:00:00,mod_dl_dst:0a:00:02:02:00:00,output=3
$ofctl add-flow s2 in_port=3,ip,nw_src=10.0.1.2,nw_dst=10.0.2.2,actions=mod_dl_src:0a:00:01:02:00:00,mod_dl_dst:0a:00:02:02:00:00,output=1

# h2 -> h1
$ofctl add-flow s2 in_port=1,ip,nw_src=10.0.2.2,nw_dst=10.0.1.2,actions=mod_dl_src:0a:00:02:02:00:00,mod_dl_dst:0a:00:01:02:00:00,output=3
$ofctl add-flow s1 in_port=3,ip,nw_src=10.0.2.2,nw_dst=10.0.1.2,actions=mod_dl_src:0a:00:02:02:00:00,mod_dl_dst:0a:00:01:02:00:00,output=1



# h3 -> h6
$ofctl add-flow s3 in_port=1,ip,nw_src=10.0.3.2,nw_dst=10.0.6.2,actions=mod_dl_src:0a:00:03:02:00:00,mod_dl_dst:0a:00:06:02:00:00,output=4
$ofctl add-flow s6 in_port=2,ip,nw_src=10.0.3.2,nw_dst=10.0.6.2,actions=mod_dl_src:0a:00:03:02:00:00,mod_dl_dst:0a:00:06:02:00:00,output=1

# h6 -> h3
$ofctl add-flow s6 in_port=1,ip,nw_src=10.0.6.2,nw_dst=10.0.3.2,actions=mod_dl_src:0a:00:06:02:00:00,mod_dl_dst:0a:00:03:02:00:00,output=2
$ofctl add-flow s3 in_port=4,ip,nw_src=10.0.6.2,nw_dst=10.0.3.2,actions=mod_dl_src:0a:00:06:02:00:00,mod_dl_dst:0a:00:03:02:00:00,output=1


for sw in s1 s2 s3 s4 s5 s6; do
    echo "==== $sw ===="
    $ofctl dump-flows $sw
    echo ""
done
