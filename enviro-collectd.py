import random
import time
import os
import signal
import sys
import logging
import argparse

import envirophat
from prometheus_client import Gauge, start_http_server


def _daemonize(pid_file, func, *args):
    """Call func in child process"""
    pid = os.fork()
    if pid > 0: # Main process
        with open(pid_file, 'w') as pid_file:
            pid_file.write(str(pid))
        sys.exit()
    elif pid == 0: # Sub Process
        func(*args)


class EnviroCollector:
    temperature = Gauge('enviro_sensing_temperature', 'Temperature reported by BMP280')
    pressure = Gauge('enviro_sensing_presure', 'Pressure reported by BMP280')
    light = Gauge('enviro_sensing_light', 'Light value reported by TCS3472')
    color = Gauge('enviro_sensing_color', 'RGB value reported by TCS3472', ['rgb'])

    def __init__(self, port: int, interval: int):
        self.interval = interval
        self.port = port
        self._running = True


    def __collect(self):
        # Create a metric to track time spent and requests made.
        current_temperature = envirophat.weather.temperature()
        current_light = envirophat.light.light()
        current_rgb = envirophat.light.rgb()
        current_pressure = envirophat.weather.pressure(unit='hPa')

        logging.debug('Current temperature: {}'.format(current_temperature))
        logging.debug('Current light value: {}'.format(current_light))
        logging.debug('Current rgb value: red={}, green={}, blue={}'.format(
            current_rgb[0], current_rgb[1], current_rgb[2])
        )
        logging.debug('Current pressure value: {} hPa'.format(current_pressure))

        # Expose temperature level
        EnviroCollector.temperature.set(current_temperature)

        # Expose light level
        EnviroCollector.light.set(current_light)

        # Expose colors
        EnviroCollector.color.labels(rgb='red').set(current_rgb[0])
        EnviroCollector.color.labels(rgb='green').set(current_rgb[1])
        EnviroCollector.color.labels(rgb='blue').set(current_rgb[2])

        # Expose pressure
        EnviroCollector.pressure.set(current_pressure)


    def start(self):
        logging.info('Start collecting data from enviro')
        start_http_server(self.port)
        while self._running:
            self.__collect()
            time.sleep(self.interval)


    def start_background(self, pid_file):
        _daemonize(pid_file, self.start)


    def stop(self, *args):
        logging.info('Trying to stop sensor data collector')
        self._running = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p', '--port', dest='port', action='store', type=int, default=9090,
                        help='Port number to start http server. Default: 9090')
    parser.add_argument('-i', '--interval', dest='interval', action='store', type=int, default=5,
                        help='Interval where the daemon get value from sensors. Default: 5 seconds')
    parser.add_argument('-d', '--daemon', dest='daemon', action='store_true', default=False,
                        help='Run job in background. Default: False')
    parser.add_argument('-f', '--log-file', dest='logfile', action='store',
                        default='/var/log/enviro-collectd.log', help='Log file. Default: /var/log/enviro-collectd.log')
    parser.add_argument('--debug', dest='debug', action='store_true', default=False,
                        help='Whether to print debug log. Default: False')
    parser.add_argument('--pid', dest='pid_file', action='store', default='/var/run/enviro-collectd.pid',
                        help='Path to pid file. Default: /var/run/enviro-collectd.pid')
    args = parser.parse_args()

    # Start up the server to expose the metrics.
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    # Configure logging
    logging.basicConfig(filename=args.logfile, level=log_level, format='%(asctime)s %(message)s')
    enviro_collector = EnviroCollector(port=args.port, interval=args.interval)

    signal.signal(signal.SIGTERM, enviro_collector.stop)
    signal.signal(signal.SIGINT, enviro_collector.stop)

    try:
        if args.daemon:
            enviro_collector.start_background(args.pid_file)
        else:
            enviro_collector.start()
    except OSError:
        print('Address already in use')
    finally:
        logging.info('Stop collecting data from enviro')
