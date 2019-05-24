### Introduction
This is a collection of tools for raspberry pi
Currently, my collection includes:

* 3 Raspberry Pi W Zero v1.1
* 1 Raspberry Pi 3B
* 1 Raspberry Pi 3B+
* Dozens of pimoroni stuffs: enviro phat, piglow, waveshare 1.44 ince LCD Hat

### Collections

1. enviro-collectd.py

**Usage**

```
$ python3 enviro-collectd.py -h
usage: enviro-collectd.py [-h] [-p PORT] [-i INTERVAL] [-d] [-f LOGFILE]
                          [--debug] [--pid PID_FILE]

Process some integers.

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Port number to start http server. Default: 9090
  -i INTERVAL, --interval INTERVAL
                        Interval where the daemon get value from sensors.
                        Default: 5 seconds
  -d, --daemon          Run job in background. Default: False
  -f LOGFILE, --log-file LOGFILE
                        Log file. Default: /var/log/enviro-collectd.log
  --debug               Whether to print debug log. Default: False
  --pid PID_FILE        Path to pid file. Default: /var/run/enviro-
                        collectd.pid

$ python3 enviro-collectd.py -d --pid enviro.pid -f enviro.log
```

Enviro phat includes various sensors.

* BMP280 temperature/pressure sensor
* TCS3472 light and RGB color sensor
* LEDS illumination
* LSM303D accelerometer/magnetometer sensor
* ADS1015 4-channel 3.3v

This python script exposes above sensor data as Prometheus Gauge metrics,
and start a local http server for Prometheus to scrape data from.

This script depends on
- python3-envirophat
- prometheus-client

Above dependencies can be installed by

```
$ curl https://get.pimoroni.com/envirophat | bash
$ sudo apt install python3-pip   # In case it is not installed
$ sudo apt install python3-envirophat
$ sudo apt install prometheus-client
```

Visit [enviro-phat Github](https://github.com/pimoroni/enviro-phat) and [Prometheus Python Client Github](https://github.com/prometheus/client_python) for more information on how to install those tools.