import sys
from time import sleep
from influxdb import InfluxDBClient
import subprocess
import re

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('temp')
regex = re.compile('=([\d\.]*)\'')

def getTemp():
    result = subprocess.check_output(['vcgencmd','measure_temp']).decode('utf-8')
    temp = regex.search(result).group(1)
    return temp

def write():
    payload = "temp,sensor=pi temperature={}".format(getTemp())
    try:
        client.write_points(payload, protocol='line')
    except Exception as e:
        sys.stderr.write("Could not write to database.\n")
        sys.stderr.write("Exception: %s" % str(e))
        sys.exit(1)
    return

if __name__=='__main__':
    print("Writing Temperature data to InfluxDB...")
    while True:
        try:
            write()
            sleep(1)
        except KeyboardInterrupt:
            sys.stderr.write("Cancelled by keyboard input.")
            sys.exit(1)
        except:
            sys.exit(1)
