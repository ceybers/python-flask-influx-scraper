#!/home/pi/testflask/venv/bin/python3
import re #regex
import requests
import datetime
import json
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('coin')

urlBase = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms=ZAR'
hourParams = ['LTC', 'DOGE', 'BTC', 'ETH', 'XRP', 'ADA', 'XMR', 'LINK']

def getHourPrices():
    results = []
    s = requests.Session()
    for param in hourParams:
        url = urlBase.format(param)
        price = s.get(url).json()['ZAR']
        time = int(datetime.datetime.now().timestamp() * 1000000000)
        results.append({ 'coin': param, 'spotPrice': price, 'timestamp': time})
    return results

def savePrices(results):
    f = open("test.json", "w")
    f.write(json.dumps(results))
    f.close()
    return

def loadPrices():
    with open('test.json', 'r') as f:
        results = json.loads(f.read())
    return results

def uploadPrices(coins):
    data = []
    for coin in coins:
        data.append("{},coin={} spotPrice={} {}".format(
            "coinPrice",
            coin['coin'],
            coin['spotPrice'],
            coin['timestamp']
        ))
    try:
        client.write_points(data, protocol='line')
    except Exception as e:
        sys.stderr.write("Could not write to database.\n")
        sys.stderr.write("Exception: %s" % str(e))
        sys.exit(1)
    return

def downloadPrices():
    results = client.query('SELECT "time","coin",LAST(spotPrice) FROM "coin"."autogen"."coinPrice" GROUP BY "coin"')
    points = results.get_points()
    for point in points:
        print(point)
    return

if __name__ == '__main__':
    results = getHourPrices()
    #savePrices(results)
    #results = loadPrices()
    uploadPrices(results)
    #downloadPrices()
    exit(0)