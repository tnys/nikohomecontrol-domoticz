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
            Domoticz.Debug('Creating domoticz device to handle on/off state')
            Domoticz.Device(Unit=self.getFirstAvailableUnit(), DeviceID=uuid, Name=name, TypeName="Switch", Image=9).Create()

        self.device = self.getDevice(uuid)

    def handleMessage(self, topic, msg):
        if self.deviceType == 'light':
            isOn = True
            if "Properties" in msg:
                if msg["Properties"][0]["Status"] == "Off":
                    isOn = False
                Domoticz.Log("Setting light to " + str(isOn))
                self.device.Update(nValue=isOn, sValue=str(isOn))
        if self.deviceType == 'generic':
            isOn = True
            if "Properties" in msg:
                if msg["Properties"][0]["BasicState"] == "Off":
                    isOn = False
                Domoticz.Log("Setting generic to " + str(isOn))
                self.device.Update(nValue=isOn, sValue=str(isOn))

    def handleCommand(self, command, level, color):
        cmd = command.upper()
        Domoticz.Log("handleCommand")
        status = "Off"
        if cmd == "ON":
            status = "On"
        payload = ""
        if self.deviceType == 'light':
            payload = json.dumps({"Method": "devices.control", "Params": [{"Devices": [{"Uuid": self.device.DeviceID, "Properties": [{"Status": status}]}]}]})
        elif self.deviceType == 'generic':
            payload = json.dumps({"Method": "devices.control", "Params": [{"Devices": [{"Uuid": self.device.DeviceID, "Properties": [{"BasicState": status}]}]}]})
        self.mqttClient.publish('hobby/control/devices/cmd', payload)
