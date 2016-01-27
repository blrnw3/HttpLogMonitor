"""
:created: 15 Jan 2016
:author: bleerodgers blr@nw3weather.co.uk
"""

import argparse

from monitor import Monitor


DEFAULT_FREQUENCY = 10


def main():
    parser = argparse.ArgumentParser(description='Monitor an http access log')
    parser.add_argument('filename', help='path to the log file')
    parser.add_argument('-f', '--frequency', type=int, help='tail frequency, in s')
    parser.add_argument('-o', '--once', action='store_true',
                        help='run once then exit (i.e. don\'t tail)')

    args = parser.parse_args()

    monitor = Monitor(args.filename)
    try:
        monitor.run(tail=not args.once, frequency=args.frequency or DEFAULT_FREQUENCY)
    except (KeyboardInterrupt, SystemExit):
        print 'HTTP Log Monitor finished'


if __name__ == '__main__':
    main()
