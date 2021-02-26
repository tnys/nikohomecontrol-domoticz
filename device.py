import Domoticz
import json
import math

class Device():
    deviceType = "Unknown"
    def __init__(self, domoticz_devices, device, mqttClient):
        self.devices = domoticz_devices
        self._register(device)
        self.mqttClient = mqttClient

    def getFirstAvailableUnit(self):
        for i in range(1, 255):
            if i not in self.devices:
                return i

    def getDevice(self, uuid):
        for unit, device in self.devices.items():
            if device.DeviceID == uuid:
                return device
    def getUnit(self):
        return self.device.Unit

    def _register(self, device):
        name = device['Name']
        uuid = device['Uuid']
        self.deviceType = device['Model']
        Domoticz.Log("Register " + name + " with devicetype " + self.deviceType)

        # for now, we just create switches. Later on, add dimmers, thermostats, ...
        if self.getDevice(uuid) == None:
            if self.deviceType == 'rolldownshutter':
                Domoticz.Debug('Creating domoticz shutter')
                Domoticz.Device(Unit=self.getFirstAvailableUnit(), DeviceID=uuid, Name=name, TypeName="Switch", Switchtype = 3, Image=9).Create()
            else:
                Domoticz.Debug('Creating domoticz device to handle on/off state')
                Domoticz.Device(Unit=self.getFirstAvailableUnit(), DeviceID=uuid, Name=name, TypeName="Switch", Image=9).Create()

        self.device = self.getDevice(uuid)

    def handleMessage(self, topic, msg):
        if self.deviceType == 'light':
            isOn = True
            if "Properties" in msg:
                for property in msg["Properties"]:
                    if "Status" in property.keys():
                        if property["Status"] == "Off":
                            isOn = False
                Domoticz.Log("Setting light to " + str(isOn))
                self.device.Update(nValue=isOn, sValue=str(isOn))
        if self.deviceType == 'rolldownshutter':
            isOn = True
            if "Properties" in msg:
                Domoticz.Log(json.dumps(msg))
                for property in msg["Properties"]:
                    if "Position" in property.keys():
                        if property["Position"] == "100":
                            isOn = False
                Domoticz.Log("Setting shutter to " + str(isOn))
                self.device.Update(nValue=isOn, sValue=str(isOn))
        if self.deviceType == 'generic':
            isOn = True
            if "Properties" in msg:
                for property in msg["Properties"]:
                    if "BasicState" in property.keys():
                        if property["BasicState"] == "Off":
                            isOn = False
                Domoticz.Log("Setting generic to " + str(isOn))
                self.device.Update(nValue=isOn, sValue=str(isOn))

    def handleCommand(self, command, level, color):
        cmd = command.upper()
        Domoticz.Log("handleCommand:" + command)
        status = "Off"
        if cmd == "ON":
            status = "On"
        payload = ""
        if self.deviceType == 'light':
            payload = json.dumps({"Method": "devices.control", "Params": [{"Devices": [{"Uuid": self.device.DeviceID, "Properties": [{"Status": status}]}]}]})
        elif self.deviceType == 'generic':
            payload = json.dumps({"Method": "devices.control", "Params": [{"Devices": [{"Uuid": self.device.DeviceID, "Properties": [{"BasicState": status}]}]}]})
        elif self.deviceType == 'rolldownshutter':
            if cmd == "ON":
                status = "Open"
            else:
                status = "Close"
            payload = json.dumps({"Method": "devices.control", "Params": [{"Devices": [{"Uuid": self.device.DeviceID, "Properties": [{"Action": status}]}]}]})
        self.mqttClient.publish('hobby/control/devices/cmd', payload)
