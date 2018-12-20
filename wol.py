#!/usr/bin/env python3
#
# First attempt at a WoL python script.
#
# We attempt IPv6 where possible and default to port 9.
# Port 7 (echo) is also defined for WoL; however, it can result
# in reflection.
#
################################################################################
import argparse
import mac_address
import netifaces
import os
import socket
import sys
import wolpw

def getIPv6Address(ipAddr, wol_socket):
   info     = socket.getaddrinfo(ipAddr, wol_socket, socket.AF_INET6)
   index    = len(info)-1
   last_tup = len(info[index])-1
   address  = info[index][last_tup]
   return address

def wol(mac, pw="", port=9):
   """ Send a WOL packet to the given MAC address """
   result = False
   WOL_PREFIX = "FFFFFFFFFFFF"
   EN0 = netifaces.gateways()['default'][netifaces.AF_INET][1]
   iface_details = netifaces.ifaddresses(EN0)

   # Check supplied mac address.
   mac   = mac_address.checkMACByteFormat(mac)
   mac   = mac_address.removeMACSeperators(mac)
   error = mac_address.verifyMACBroadcastLength(mac)

   # If we're called from the command line, raise an exception.
   if (len(error) > 0):
      if 'tkinter' not in sys.modules:
         raise ValueError(error)
      else:
         return result
 
   # Setup the magic packet.
   magic_packet = ''.join([WOL_PREFIX, mac * 16])

   # If a PW was provided, append it to the packet
   if (len(pw) > 0):
      magic_packet = magic_packet + pw

   # Pack the bytes from the magic packet string.
   send_data = bytes.fromhex(magic_packet)

   # Broadcast it to the LAN.
   if (socket.has_ipv6 == True):
      # socket.IPPROTO_IPV6 may not be defined on Windows, hardcode for now
      SOCKET_OP = 41
      if "Windows" in os.environ.get('OS',''):
         WOL_IPV6 = "ff02::1"
      else :
         WOL_IPV6 = "ff02::1%"+EN0
         SOCKET_OP = socket.IPPROTO_IPV6

      # Get Host device port bindings
      IPADDR = iface_details.get(netifaces.AF_INET6)[0].get('addr')
      HOST_BIND = getIPv6Address(IPADDR, 0)

      # Get Remote device port info 
      DEST_ADDR = getIPv6Address(WOL_IPV6, port)

      # Send the data
      sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
      sock.setsockopt(SOCKET_OP, socket.IPV6_MULTICAST_HOPS, 1)
      sock.bind(HOST_BIND)
      sock.sendto(send_data, DEST_ADDR)
      sock.close()
      result = True
   else:
      WOL_IPV4 = iface_details.get(netifaces.AF_INET)[0].get("broadcast")
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      sock.sendto(send_data, (WOL_IPV4, port))
      sock.close()
      result = True
   return result

if __name__ == '__main__':
   parser = argparse.ArgumentParser()
   parser.add_argument("mac_address",
                       help="The MAC address to send the magic packet",
                       type=str)
   parser.add_argument("-p", help="Port to send the magic packet (default 9)",
                       type=int,
                       action="store",
                       default=9,
                       dest="port")
   parser.add_argument("-pw", help="WoL password (no 0x prefix)",
                       type=str,
                       action="store",
                       default="",
                       dest="password")
   args = parser.parse_args()
   if (wolpw.validPWFormat(args.password)):
      wol(args.mac_address, port=args.port, pw=args.password)
   else:
      print("Invalid WoL Password")
