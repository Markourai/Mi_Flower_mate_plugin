import urllib.request
import base64
import time
from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY

from miflora.backends.bluepy import BluepyBackend
from miflora.backends.gatttool import GatttoolBackend

# Settings for the domoticz server

# Forum see: http://domoticz.com/forum/viewtopic.php?f=56&t=13306&hilit=mi+flora&start=20#p105255
domoticzserver   = "127.0.0.1:8080"
domoticzusername = "myuser"
domoticzpassword = "mypassword"

# So id devices use: sudo hcitool lescan

# Sensor IDs

# Create 4 virtual sensors in dummy hardware
# type temperature
# type lux
# type percentage (moisture)
# type custom (fertility)

base64string = base64.encodestring(('%s:%s' % (domoticzusername, domoticzpassword)).encode()).decode().replace('\n', '')

def domoticzrequest (url):
  request = urllib.request.Request(url)
  request.add_header("Authorization", "Basic %s" % base64string)
  response = urllib.request.urlopen(request)
  return response.read()

def update(address,idx_moist,idx_temp,idx_lux,idx_cond):

    poller = MiFloraPoller(address, GatttoolBackend)

    # reading error in poller (happens sometime, you go and bug the original author):

    loop = 0
    try:
        temp = poller.parameter_value(MI_TEMPERATURE)
    except:
        temp = 201

    while loop < 2 and temp > 200:
        print("Patched: Error reading value retry after 5 seconds...\n")
        time.sleep(5)
        #poller = MiFloraPoller(address, GatttoolBackend)
        loop += 1
        try:
            temp = poller.parameter_value(MI_TEMPERATURE)
        except:
            temp = 201

    if temp > 200:
        print("Patched: Error reading value\n")
        return

    global domoticzserver

    print("Mi Flora: " + address)
    print("Firmware: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Temperature: {}°C".format(poller.parameter_value(MI_TEMPERATURE)))
    print("Moisture: {}%".format(poller.parameter_value(MI_MOISTURE)))
    print("Light: {} lux".format(poller.parameter_value(MI_LIGHT)))
    print("Fertility: {} uS/cm?".format(poller.parameter_value(MI_CONDUCTIVITY)))
    print("Battery: {}%".format(poller.parameter_value(MI_BATTERY)))

    val_bat  = "{}".format(poller.parameter_value(MI_BATTERY))

    # Update temp
    val_temp = "{}".format(poller.parameter_value(MI_TEMPERATURE))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_temp + "&nvalue=0&svalue=" + val_temp + "&battery=" + val_bat)

    # Update lux
    val_lux = "{}".format(poller.parameter_value(MI_LIGHT))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_lux + "&svalue=" + val_lux + "&battery=" + val_bat)

    # Update moisture
    val_moist = "{}".format(poller.parameter_value(MI_MOISTURE))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_moist + "&svalue=" + val_moist + "&battery=" + val_bat)

    # Update fertility
    val_cond = "{}".format(poller.parameter_value(MI_CONDUCTIVITY))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_cond + "&svalue=" + val_cond + "&battery=" + val_bat)
    time.sleep(1)

# format address, moist (%), temp (°C), lux, fertility
# Example / test

print("\n1: Pointsettia")
update("C4:7C:8D:67:4B:28","117","118","119","120")

print("\n2: Olivier")
update("C4:7C:8D:62:48:40","121","122","123","124")

print("\n3: Bonsai")
update("C4:7C:8D:62:47:D0","107","108","109","110")
