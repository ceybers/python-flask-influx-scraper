#!/home/pi/testflask/venv/bin/python3
import re #regex
import sys
from time import sleep
import datetime
import json
from influxdb import InfluxDBClient
import dateutil

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('network')

# getNetRead for Dongle
net_data_fn = "/proc/net/dev"
reProcNetDevA = re.compile('^.*wwan0.*$', re.MULTILINE)
reProcNetDevB = re.compile('(\s+\d+)')

def getTimestamp():
    date = datetime.datetime.utcnow()
    dateUTC = date.replace(tzinfo=dateutil.tz.gettz('UTC'))
    timestamp = int(dateUTC.timestamp() * 1000000000)
    return timestamp

def getNetRead():
    with open(net_data_fn) as f:
        content = f.read()
    wwanTraffic = reProcNetDevB.findall(reProcNetDevA.search(content).group(0))
    wwanRX = int(wwanTraffic[0])
    wwanTX = int(wwanTraffic[8])
    payload = "throughput,device=e392 rx={}i,tx={}i {}".format(wwanRX, wwanTX, getTimestamp())
    return payload

def upload(payload):
    try:
        client.write_points(payload, protocol='line')
    except Exception as e:
        sys.stderr.write("Could not write to database.\n")
        sys.stderr.write("Exception: %s" % str(e))
        sys.exit(1)
    return

if __name__=='__main__':
    print("Writing Network stats (e392) to InfluxDB...")
    while True:
        try:
            data = getNetRead()
            upload(data)
            sleep(1)
        except KeyboardInterrupt:
            sys.stderr.write("Cancelled by keyboard input.")
            sys.exit(0)
        except:
            sys.stderr.write("Exception in main.")
            sys.exit(1)