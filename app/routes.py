from flask import render_template
from app import app
from influxdb import InfluxDBClient
import dateutil.parser

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('ups')

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'fellow robot'}
    posts = [
        {
            'author': {'username': 'BTC'},
            'body': '800000ZAR'
        },
        {
            'author': {'username': 'ETH'},
            'body': '40000ZAR'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/power')
def power():
    user = {'username': 'fellow robot'}
    results = client.query('SELECT * FROM "ups"."autogen"."INA219" ORDER BY time DESC LIMIT 10')
    points = results.get_points()
    data = []
    for point in points:
        _datetime = dateutil.parser.isoparse(point['time']).strftime('%Y-%m-%d %H:%M:%S')
        data.append({'time': _datetime, 'current': point['current'], 'voltage': point['voltage'], 'power': point['power'], 'percent': point['percent']})
    return render_template('power.html', title='Power', user=user, data=data)

@app.route('/coin')
def coin():
    # results = client.query('SELECT * FROM "coin"."autogen"."coinPrice"')
    results = client.query('SELECT "time","coin",LAST(spotPrice) FROM "coin"."autogen"."coinPrice" GROUP BY "coin"')
    points = results.get_points()
    data = []
    for point in points:
        _datetime = dateutil.parser.isoparse(point['time']).strftime('%Y-%m-%d %H:%M:%S')
        data.append({'time': _datetime, 'coin': point['coin'], 'spotPrice': point['last']})
    return render_template('coin.html', title='Coin', data=data)

@app.route('/etf/<path:units>')
def etf(units):
    unitsSplit = units.split(',')
    allUnits = []
    for unit in unitsSplit:
        results = client.query('SELECT "time","unit","closePrice" FROM "coin"."autogen"."etf" WHERE "unit" = \'' + unit + '\' ORDER BY time DESC LIMIT 30')
        points = results.get_points()
        json = []
        for point in points:
            _datetime = dateutil.parser.isoparse(point['time']).strftime('%Y-%m-%d')
            json.append("{\"dateTime\":\"%s\",\"value\":%f}" % (_datetime, 100 * point['closePrice']))
        json2 = ','.join(json)
        oneUnit = "{\"ticker\":\"%s\",\"price\":[%s]}" % (unit, json2)
        allUnits.append(oneUnit)
    allUnitsText = ','.join(allUnits)
    allUnitsText = '[' + allUnitsText + ']'
    #return render_template('etf.html', title='ETF', ticker=unit, data=allUnitsText)
    return allUnitsText, 200, {'Content-Type': 'text/json; charset=utf-8'}


@app.route('/temp')
def temp():
    results = client.query('SELECT * FROM "temp"."autogen"."temp" ORDER BY time DESC LIMIT 25')
    points = results.get_points()
    data = []
    for point in points:
        _datetime = dateutil.parser.isoparse(point['time']).strftime('%Y-%m-%d %H:%M:%S')
        data.append({'time': _datetime, 'sensor': point['sensor'], 'value': point['temperature']})
    return render_template('temp.html', title='Temp', data=data)

if __name__ == '__main__':
    app.run(debug = True)