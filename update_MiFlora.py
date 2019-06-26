import sys
import getopt
import logging
import urllib.request
import base64
import time
from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY

from miflora.backends.bluepy import BluepyBackend
from miflora.backends.gatttool import GatttoolBackend

logging.basicConfig(filename='/home/pi/domo_flora.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

_debug = 0

# Settings for the domoticz server
# Forum see: http://domoticz.com/forum/viewtopic.php?f=56&t=13306&hilit=mi+flora&start=20#p105255
domoticzserver   = "127.0.0.1:8080"
domoticzusername = "myuser"
domoticzpassword = "mypassword"

base64string = base64.encodebytes(('%s:%s' % (domoticzusername, domoticzpassword)).encode()).decode().replace('\n', '')

# Prepare domoticz request with authorization
def domoticzrequest (url):
  request = urllib.request.Request(url)
  request.add_header("Authorization", "Basic %s" % base64string)
  response = urllib.request.urlopen(request)
  return response.read()

# Update function to get information
# Format: address, moist (%), temp (°C), lux, fertility, comment
def update(address,idx_moist,idx_temp,idx_lux,idx_cond, comment):

    logging.info("Begin polling data for: " + address)
    poller = MiFloraPoller(address, BluepyBackend)

    # reading error in poller (happens sometime, you go and bug the original author):
    loop = 0
    try:
        temp = poller.parameter_value(MI_TEMPERATURE)
    except:
        temp = 201

    while loop < 2 and temp > 200:
        logging.warning("Patched: Error reading value retry after 5 seconds for :" + address)
        time.sleep(5)
        #poller = MiFloraPoller(address, GatttoolBackend)
        loop += 1
        try:
            temp = poller.parameter_value(MI_TEMPERATURE)
        except:
            temp = 201

    if temp > 200:
        logging.error("Patched: Error reading value for :" + address")
        return

    global domoticzserver
    if _debug == 1:
        logging.debug("Plant: " + comment)
        logging.debug("Mi Flora: " + address)
        logging.debug("Firmware: {}".format(poller.firmware_version()))
        logging.debug("Name: {}".format(poller.name()))
        logging.debug("Temperature: {}°C".format(poller.parameter_value(MI_TEMPERATURE)))
        logging.debug("Moisture: {}%".format(poller.parameter_value(MI_MOISTURE)))
        logging.debug("Light: {} lux".format(poller.parameter_value(MI_LIGHT)))
        logging.debug("Fertility: {} uS/cm?".format(poller.parameter_value(MI_CONDUCTIVITY)))
        logging.debug("Battery: {}%".format(poller.parameter_value(MI_BATTERY)))

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

def usage():
  print('Usage: '+sys.argv[0]+' -a <mac-address> -m <moisture-id> -t <temperature-id> -l <lux-id> -f <fertility-id> -c [comment]')

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ha:m:t:l:f:c:d", ["help", "address=", "moisture=", "temp=", "lux=", "fertility=", "comment="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    if len(argv) == 0:
        print("Missing arguments")
        usage()
        sys.exit(2)

    _address = ""
    _moisture = ""
    _temp = ""
    _lux = ""
    _fertility = ""
    _comment = ""

    for opt, arg in opts:
        #print("arg: " + arg + ", opt: " + opt)
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--debug"):
            global _debug
            _debug = 1
        elif opt in ("-a", "--address"):
            _address = arg
        elif opt in ("-m", "--moisture"):
            _moisture = arg
        elif opt in ("-t", "--temp"):
            _temp = arg
        elif opt in ("-l", "--lux"):
            _lux = arg
        elif opt in ("-f", "--fertility"):
            _fertility = arg
        elif opt in ("-c", "--comment"):
            _comment = arg
        else:
            assert False, "Unhandled option"
    if _debug == 1:
        logging.debug("update of " + _comment + ": " + _address + ", " + _moisture + ", " + _temp + ", " + _lux + ", " + _fertility)
    update(_address, _moisture, _temp, _lux, _fertility, _comment)

if __name__ == "__main__":
    main(sys.argv[1:])
