# ARP methods
# These routines are for processing ARP output to collect host/IP/MAC 
# information
################################################################################

import mac_address
import os
import subprocess

def getMACAddresses():
   """Get the name and MAC address of the systems in the arp table"""

   p = subprocess.Popen(["arp", "-a"], stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)

   out, err = p.communicate()
   readable_output = out.decode("utf-8")
   list_of_systems = readable_output.split()

   if "Windows" in os.environ.get('OS',''):
      return getWindowsMACAddresses(list_of_systems)
   else :
      return getUnixMACAddresses(list_of_systems)

def getWindowsMACAddresses(list_of_systems):
   """Get the name and MAC address of the systems in the Windows arp table"""

   table = dict()
   if (len(list_of_systems) > 6) :
      for i in range(2, len(list_of_systems)):
         if (list_of_systems[i] == 'static' or \
             list_of_systems[i] == 'dynamic'):
            name = list_of_systems[i-2]
            addr = list_of_systems[i-1]
            if not name.startswith(("255", "224")) :
               addr = mac_address.checkMACByteFormat(addr) 
               table.update({name:addr})

   return table

def getUnixMACAddresses(list_of_systems):
   """Get the name and MAC address of the systems in the Unix arp table"""

   table = dict()
   if (len(list_of_systems) > 6) :
      for i in range(1, len(list_of_systems)):
         if (list_of_systems[i][0] == '(' and \
             list_of_systems[i][len(list_of_systems[i])-1] == ')'):
            name = list_of_systems[i-1]
            addr = list_of_systems[i+2]
            addr = mac_address.checkMACByteFormat(addr) 
            table.update({name:addr})

   return table
