# WOL PW methods
################################################################################

import re

def validPWFormat(pw) :
   """Check if the provided pw is of a valid format"""
   result = False
   pwlen = len(pw)
   if (pwlen == 0) :
      result = True
   elif (pwlen == 4 or pwlen == 6) :
      if (re.match('^[0-9a-fA-F]*$', pw)) :
         result = True
   return result
