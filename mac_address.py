# MAC address methods
# Routines to manipulate and verify MAC address values
################################################################################
import re

def checkMACByteFormat(mac):
   """Correct for single byte entries"""
   length = len(mac)

   # Should be at least 11 chars long
   if (length < 11):
      return

   nonByteChrs = ''.join(re.split(r'[0-9a-fA-F]', mac))
   
   # Should have at least 5 seperators
   numSep = len(nonByteChrs)
   if (numSep < 5):
      return

   # assume uniformity
   sep = nonByteChrs[0]
   indexes = [m.start() for m in re.finditer(sep, mac)]

   # Correct 4 bit entries
   if (indexes[0] < 2):
       mac="0"+mac

   for i in range(1, len(indexes)) :
       if (indexes[i] - indexes[i-1] < 3):
          mac = mac[:i*3] +'0' + mac[i*3:]

   if (length - indexes[len(indexes)-1] < 3):
      mac = mac[:numSep*3] +'0' + mac[numSep*3:]

   return mac


def removeMACSeperators(mac):
   """Filter seperators from MAC-48 or EUI-48 style addresses"""

   # Since we're not sure what seperator style the user may have entered,
   # we'll just go off the MAC-48/EUI-48 length

   if (len(mac) == 12 + 5): # 12 for the bytes, 5 for the seperators
      sep = mac[2]
      mac = mac.replace(sep, '')

   return mac


def verifyMACBroadcastLength(mac):
   """Validate length of MAC-48 or EUI-48 style addresses"""
   error = ""
   if (len(mac) != 12):
       error = "Incorrect MAC address format"

   return error
