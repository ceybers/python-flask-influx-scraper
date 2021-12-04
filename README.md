# python-flask-influx-scraper
Python scrapers, storing data in InfluxDB, presented via Flask

## Scrapers
* writeCryptoHourtoDB - Saves a selection of crypto prices from cryptocompare.com to InfluxDB
* writeETFDaytoDB - Scrapes www.satrix.co.za for daily ETF prices
* writeNetWWANtoDB - Saves network throughput stats from my Raspberry Pi to InfluxDB
* writeTemptoDB - Saves Raspberry Pi temperature to InfluxDB
* writeUPStoDB - Saves UPS stats from a Waveshare UPS HAT for Raspberry Pi to InfluxDB

## Useful bash aliases
```
alias goflask='nohup flask run --host 0.0.0.0 > log.txt 2>&1 &'
alias stopflask='ps aux | grep bin/flask | awk "{print $2}" | head -1 | xargs kill'
alias getetf='wget -q -O /mnt/ext/incoming/etf.json http://192.168.8.2:5000/etf/STXFIN:SJ,STXNDQ:SJ,STX500:SJ'
```