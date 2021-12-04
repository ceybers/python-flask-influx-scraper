#!/home/pi/testflask/venv/bin/python3
import re #regex
import requests
from datetime import datetime
import json
from influxdb import InfluxDBClient
import dateutil 

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('coin')

fetchList = '''[
    { "unitName":"STXFIN:SJ", "urlParam":"23"},
    { "unitName":"STXRES:SJ", "urlParam":"27"},
    { "unitName":"STXIND:SJ", "urlParam":"24"},
    { "unitName":"STX500:SJ", "urlParam":"46"},
    { "unitName":"STXNDQ:SJ", "urlParam":"51"},
    { "unitName":"STXDIV:SJ", "urlParam":"22"}
]'''

url = "https://satrix.co.za/products/product-details?id={}&TabSelection=ETF"
regexNAV = re.compile('(?=Net Asset Value).*\s*.*R (\d*.\d*)')
regexAsOn = re.compile('Investor Information<\/h1>\s+<h3>As On (\d{2} \w+ \d{4})<')

def getPrice(s, unitName, urlParam):
    #f = open("/home/pi/satrix.txt")
    #prices = f.read()
    #price = regexNAV.search(prices).group(1)
    urlWithParam = url.format(urlParam)
    prices = s.get(urlWithParam).text
    price = regexNAV.search(prices).group(1)
    dateText = regexAsOn.search(prices).group(1)
    date = dateutil.parser.parse(dateText, ignoretz=True)
    dateUTC = date.replace(tzinfo=dateutil.tz.gettz('UTC'))
    timestamp = int(dateUTC.timestamp() * 1000000000)
    payload = "etf,unit={} closePrice={} {}".format(unitName, price, timestamp)
    return payload

def getPrices():
    s = requests.Session()
    payloads = ""
    for f in json.loads(fetchList):
        payload = getPrice(s, f['unitName'], f['urlParam'])
        payloads += payload + '\n'
    return payloads

def savePrices(results):
    f = open("test.json", "w")
    f.write(json.dumps(results))
    f.close()
    return

def loadPrices():
    with open('test.json', 'r') as f:
        results = json.loads(f.read())
    return results

def uploadPrices(payload):
    try:
        client.write_points(payload, protocol='line')
    except Exception as e:
        sys.stderr.write("Could not write to database.\n")
        sys.stderr.write("Exception: %s" % str(e))
        sys.exit(1)
    return

def downloadPrices():
    results = client.query('SELECT "time","unit",LAST(closePrice) FROM "etf" GROUP BY "unit"')
    points = results.get_points()
    for point in points:
        print(point)
    return

if __name__ == '__main__':
    results = getPrices()
    #savePrices(results)
    #results = loadPrices()
    uploadPrices(results)
    #downloadPrices()
    exit(0)