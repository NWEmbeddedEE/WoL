#!/usr/bin/env python3
#  WOL Dialog
#    This script wraps a UI around our wol.py script.
################################################################################

import json
import os.path
import tkinter
import read_arp
import wol
import wolpw
import tkinter as tk

from tkinter import Button
from tkinter import Entry
from tkinter import Frame
from tkinter import Label
from tkinter import messagebox
from tkinter import OptionMenu
from tkinter import StringVar
from os.path import expanduser

# Define text for our labels
NAME_LBL = "System Name"
MAC_LBL  = "MAC Address"
PW_LBL   = "WoL PW(Optional)"
SYS_LBL  = "Detected Systems"

# Define Constants
LAST_WOL    = "LWOL"
SYSTEM_LIST = "LIST"
NAME_ENTRY  = 0
MAC_ENTRY   = 1
PW_ENTRY    = 2

class WOLWindow(Frame):

   # Class variables
   file_name  = os.path.join(expanduser("~"), ".wolsystems")

   def __init__(self,parent=None):
      Frame.__init__(self,parent)
      self.parent = parent
      self.pack()
      self.winfo_toplevel().title("Send WoL")

      # Instance variables
      self.last_wol   = ""
      self.entries    = []
      self.choices    = dict()
      self.wol_status = None

      self.setFields(root)
      self.prepackEntries()

      # Now that the dialog is packed, set the window dimensions.
      # Bind the enter/return key for sending a magic packet.
      root.update_idletasks()
      root.minsize(root.winfo_width(), root.winfo_height())
      root.maxsize(root.winfo_width(), root.winfo_height())
      root.bind('<Return>', self.prepWOL)
 

   def prepackEntries(self) :
      """Enter the system data for the last sent WoL"""
      if (len(self.last_wol) > 0) :
         mac = self.choices[self.last_wol]
         self.entries[NAME_ENTRY][1].insert(10,self.last_wol)
         self.entries[MAC_ENTRY][1].insert(10,mac)


   def optSelected(self, name):
      """Populate Entry fields with OptionMenu selection"""
      mac = self.choices.get(name, "")
      self.entries[NAME_ENTRY][1].delete(0, 'end')
      self.entries[NAME_ENTRY][1].insert(10,name) 
      self.entries[MAC_ENTRY][1].delete(0, 'end')
      self.entries[MAC_ENTRY][1].insert(10,mac) 


   def setFields(self, root):
      """Setup the widgets for the dialog"""
 
      # Add System Name Edit First (NAME_ENTRY=0)
      row = Frame(root)
      lab = Label(row, width=15, text=NAME_LBL, anchor='w')
      name_entry = Entry(row)
      row.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)
      lab.pack(side=tkinter.LEFT)
      name_entry.pack(side=tkinter.RIGHT, expand=tkinter.YES, fill=tkinter.X)
      self.entries.append((lab, name_entry))

      # Add MAC Edit Second (MAC_ENTRY=1)
      row = Frame(root)
      lab = Label(row, width=15, text=MAC_LBL, anchor='w')
      mac_entry = Entry(row)
      row.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)
      lab.pack(side=tkinter.LEFT)
      mac_entry.pack(side=tkinter.RIGHT, expand=tkinter.YES, fill=tkinter.X)
      self.entries.append((lab, mac_entry))

      # Add PW Edit Third (PW_ENTRY=2)
      row = Frame(root)
      lab = Label(row, width=15, text=PW_LBL, anchor='w')
      pw_entry = Entry(row)
      row.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)
      lab.pack(side=tkinter.LEFT)
      pw_entry.pack(side=tkinter.RIGHT, expand=tkinter.YES, fill=tkinter.X)
      self.entries.append((lab, pw_entry))

      # Add System Dropdown Selection
      self.choices = self.getKnownSystems()
      self.selected_host = StringVar(root)
      if (len(self.choices) > 0) :
         self.selected_host.set(list(self.choices.keys())[0])

      row = Frame(root)
      lab = Label(row, width=15, text=SYS_LBL, anchor='w')
      self.host_options = OptionMenu(row, self.selected_host, *self.choices.keys(), 
                           command=self.optSelected)
      row.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)
      lab.pack(side=tkinter.LEFT)
      self.host_options.pack(side=tkinter.RIGHT, expand=tkinter.YES, fill=tkinter.X)

      # Add Quit and Send buttons
      row = Frame(root)
      row.pack(side=tkinter.TOP, fill=tkinter.X, padx=5, pady=5)
      sendBtn = Button(row, text='Send', command=(lambda : self.prepWOL())) 
      sendBtn.pack(side=tkinter.RIGHT, padx=5, pady=5)
      quitBtn = Button(row, text='Quit', command=root.quit)
      quitBtn.pack(side=tkinter.LEFT, padx=5, pady=5)
 
      # Add Status Label
      self.wol_status = StringVar(root)
      self.wol_status.set("")
      status = Label(row, width=15, textvariable=self.wol_status, 
                     anchor=tkinter.CENTER)
      status.pack(side=tkinter.TOP, padx=5, pady=5)


   def getKnownSystems(self) :
      """Return the list of known systems"""
      systems = dict() 

      # Get Saved Systems. 
      if (os.path.exists(self.file_name)) :
         with open(self.file_name, 'r') as fp:
            json_data     = json.loads(fp.read())
            self.last_wol = json_data[LAST_WOL]
            systems       = json_data[SYSTEM_LIST]

      # Get Detected Systems.
      detected = read_arp.getMACAddresses()
 
      # Append newly detected systems to the list
      for key, value in detected.items():
         if (key not in systems) :
            systems[key] = value

      # Remove Entries we do not care about.
      if ("?" in systems) :
          del systems["?"]

      return systems


   def sendWOL(self, name, mac, pw):
      # The user may have edited a new name for an entry, save it if needed.
      if (name not in self.choices) :
         self.choices[name] = mac
         self.host_options["menu"].delete(0, "end")
         for hname in self.choices.keys():
            self.host_options["menu"].add_command(label=hname, command=tk._setit(self.selected_host, hname , self.optSelected))
      # Save off our names list
      json_data = { LAST_WOL : name, SYSTEM_LIST : self.choices }
      with open(self.file_name, 'w') as fp:
         json.dump(json_data, fp)

      #send the WOL Packet
      result = wol.wol(mac, pw=pw)
      if (result == True):
         self.wol_status.set("Packet Sent")
      else : 
         self.wol_status.set("Faild To Send")


   def prepWOL(self, event=None):
      mac  = self.entries[MAC_ENTRY][1].get()
      name = self.entries[NAME_ENTRY][1].get()
      pw   = self.entries[PW_ENTRY][1].get()
      if (wolpw.validPWFormat(pw) == False) :
         messagebox.showinfo("Password", "Password is not valid.")
      elif (mac == "") :
         messagebox.showinfo("MAC Address", "Need to provide a MAC address.")
      elif (name == "") :
         messagebox.showinfo("System Name", "Need to provide a system name.")
      else :
         self.sendWOL(name, mac, pw)


if __name__ == '__main__':
   root = tkinter.Tk()
   WOLWindow(root)
   root.lift()
   root.attributes('-topmost',True)
   root.mainloop()
