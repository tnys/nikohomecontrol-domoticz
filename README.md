# nikohomecontrol-domoticz
A plugin to have Niko Home Control talk to Domoticz.

Just create a folder inside the plugins folder of Domoticz, and add all files.  Within Domoticz, go to hardware and add Niko Home Control. Make sure your Niko Home Control Smart Hub or Connected Controller has a fixed IP address within your network, and specify the IP address in the Niko Home Control hardware configuration within Domoticz. In order to get the password, you need to enable the Hobby API within the Niko Home Control app.

Currently only supports On/Off switches, Virtual Outputs and Roller shutters. Using the Virtual Outputs, you can connect Niko RF switches to Domoticz switches, and have those switches trigger other switches.

As soon as I have a Niko Dimmer, Double Switch and Smart Socket they'll be added too. 
