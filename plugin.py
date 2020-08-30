# Python Plugin MQTT Subscribe Example
#
# Author: Dnpwwo
#
"""
<plugin key="NHC" name="Niko Home Control Bridge" author="tnys" version="1.0.0" externallink="https://niko.eu/">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Password" label="Password" width="200px"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import random
import json
from mqtt import MqttClient
from device import Device

class BasePlugin:
    enabled = False
    mqttConn = None
    counter = 0

    def __init__(self):
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        DumpConfigToLog()
        self.devices = {}

        Parameters["Username"]="hobby"
        Parameters["Port"]="8884"
        Parameters["Protocol"]="MQTTS"

        mqtt_server_address = Parameters["Address"].strip()
        mqtt_server_port = Parameters["Port"].strip()
        self.mqttClient = MqttClient(mqtt_server_address, mqtt_server_port, "NHCDomoticz", self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onCommand(self, Unit, Command, Level, Hue):
        for uuid, device in self.devices.items():
            if device.getUnit() == Unit:
                device.handleCommand(Command, Level, Hue)

    #MQTT forwards..
    def onConnect(self, Connection, Status, Description):
        self.mqttClient.onConnect(Connection, Status, Description)

    def onMessage(self, Connection, Data):
        self.mqttClient.onMessage(Connection, Data)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onHeartbeat(self):
        self.mqttClient.onHeartbeat()

    # MQTT stuff
    def onMQTTConnected(self):
        self.mqttClient.subscribe(['hobby/control/devices/rsp'])
        self.mqttClient.subscribe(['hobby/control/devices/evt'])
        self.mqttClient.subscribe(['hobby/control/devices/err'])


        # fetch all devices
        self.mqttClient.publish('hobby/control/devices/cmd', '{"Method": "devices.list"}')

    def onMQTTDisconnected(self):
        Domoticz.Log("onMQTT disconnected")

    def onMQTTSubscribed(self):
        Domoticz.Log("onMQTTSubscribed")




    def onMQTTPublish(self, topic, message):
        if topic == "hobby/control/devices/rsp":
            if message["Params"]:
                nhcDeviceIDs = []
                if message["Params"][0]["Devices"]:
                    for device in message["Params"][0]["Devices"]:
                        if device["Type"]=="action":
                            uuid = device["Uuid"]
                            self.devices[uuid] = Device(Devices, device, self.mqttClient)
                            self.devices[uuid].handleMessage(topic, device)
        if topic == "hobby/control/devices/evt":
            if message["Method"] == "devices.status":
                if message["Params"]:
                    if message["Params"][0]["Devices"]:
                        for device in message["Params"][0]["Devices"]:
                            uuid = device["Uuid"]
                            if uuid in self.devices:
                                self.devices[uuid].handleMessage(topic, device)
        if topic == "hobby/control/devices/err":
            Domoticz.Log("Err")







global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

def DumpDictionaryToLog(theDict, Depth=""):
    if isinstance(theDict, dict):
        for x in theDict:
            if isinstance(theDict[x], dict):
                Domoticz.Log(Depth+"> Dict '"+x+"' ("+str(len(theDict[x]))+"):")
                DumpDictionaryToLog(theDict[x], Depth+"---")
            elif isinstance(theDict[x], list):
                Domoticz.Log(Depth+"> List '"+x+"' ("+str(len(theDict[x]))+"):")
                DumpListToLog(theDict[x], Depth+"---")
            elif isinstance(theDict[x], str):
                Domoticz.Log(Depth+">'" + x + "':'" + str(theDict[x]) + "'")
            else:
                Domoticz.Log(Depth+">'" + x + "': " + str(theDict[x]))

def DumpListToLog(theList, Depth):
    if isinstance(theList, list):
        for x in theList:
            if isinstance(x, dict):
                Domoticz.Log(Depth+"> Dict ("+str(len(x))+"):")
                DumpDictionaryToLog(x, Depth+"---")
            elif isinstance(x, list):
                Domoticz.Log(Depth+"> List ("+str(len(theList))+"):")
                DumpListToLog(x, Depth+"---")
            elif isinstance(x, str):
                Domoticz.Log(Depth+">'" + x + "':'" + str(theList[x]) + "'")
            else:
                Domoticz.Log(Depth+">'" + x + "': " + str(theList[x]))
