#!/usr/bin/env python3

import sys
import socket as sock
import logging as log
import argparse

from scapy.all import *

class RawSocketListener():
    MAX_RECV_SIZE = 1024
    def __init__(self, handler, middlebox_port, iface_name, blacklist):
        self.handler = handler
        self.middlebox_port = middlebox_port
        self.iface_name = iface_name
        self.blacklist = blacklist
        self.listener = sock.socket(sock.AF_PACKET, sock.SOCK_RAW, sock.ntohs(0x0003))

    def listen_forever(self):
        print(f"Listening on middlebox port {self.middlebox_port}")
        while True:
            try:
                message = self.listener.recv(self.MAX_RECV_SIZE)
            except KeyboardInterrupt:
                print("Shutting down!")
                return None

            self.handler(message, self.middlebox_port, self.iface_name, self.blacklist)

def l2_handler(message, middlebox_port, iface_name, blacklist):
    eth_frame = Ether(message)
    if eth_frame.haslayer(UDP) and eth_frame[UDP].dport == middlebox_port\
            and eth_frame[IP].ttl == 64:
        print(f"Received a UDP packet with destination port {middlebox_port}")
        payload = eth_frame[Raw].load
        decoded_payload = payload.decode("utf-8")

        # Drop packet if payload contains any blacklisted keyword
        for keyword in blacklist:
            if keyword in decoded_payload:
                print(f"Dropping packet: payload contains blacklisted keyword '{keyword}'")
                return

        eth_frame[Raw].load = bytes(
                decoded_payload + " from the middlebox", "utf-8")
        eth_frame[IP].ttl -= 1
        eth_frame[IP].chksum = None
        eth_frame[UDP].chksum = None
        eth_frame[IP].len = None
        eth_frame[UDP].len = None
        eth_frame = Ether(bytes(eth_frame))
        eth_frame.show2()
        print(f"Modified the UDP payload. Sending the packet: "
              f"{eth_frame[IP].src}:{eth_frame[UDP].sport} -> "
              f"{eth_frame[IP].dst}:{eth_frame[UDP].dport}")
        sendp(eth_frame, iface=iface_name)

def main():
    parser = argparse.ArgumentParser(
            description="Read UDP packets sent to the middlebox port, append "
                        "the message to their payload and then send them on to the "
                        "destination specified in their IP header.")
    parser.add_argument("middlebox_port", metavar="middlebox_port", type=int,
            help="The UDP port that the middlebox will listen on, "
                 "should be the same as the port that the UDP server is listening on.")
    parser.add_argument("iface_name", metavar="iface_name",
            help="The name of the interface on the middlebox host. For example,"
                 " if you are using h3 as the middlebox host then the name of the"
                 " interface should be h3-eth0.")
    args = parser.parse_args()

    blacklist = []
    try:
        with open("blacklist.txt", 'r') as f:
            blacklist = f.read().strip().split(",")
        print(f"Loaded blacklist: {blacklist}")
    except Exception as e:
        print(f"Error loading blacklist: {e}")
        sys.exit(1)

    the_server = RawSocketListener(l2_handler, args.middlebox_port, args.iface_name, blacklist)
    the_server.listen_forever()


if __name__ == "__main__":
    main()
