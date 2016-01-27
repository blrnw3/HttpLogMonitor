"""
:created: 15 Jan 2016
:author: bleerodgers blr@nw3weather.co.uk
"""

import random

from datetime import datetime


class ApacheLogEmulator(object):
    """
    Very basic emulator for logging http traffic from an Apache web server
    """

    def __init__(self, log_path):
        self.log_path = log_path

    def emulate(self, count):
        lines = []
        for i in xrange(count):
            lines.append(
                self._get_record()
            )
        self._write_lines(lines)

    def _get_record(self):
        fields = [
            self._random_ip(),  # host
            '-',  # ident
            '-',  # authuser
            self._current_date(),  # date
            self._random_request(),  # request
            self._random_status(),  # status
            str(random.randint(0, 10000)),  # bytes
            '"http://www.google.com"',  # referrer
            '"Mozilla/5.0 (compatible; ApacheLogBot/0.1;)"'  # user agent string
        ]
        return ' '.join(fields) + '\n'

    def _write_lines(self, data):
        with open(self.log_path, 'a') as f:
            f.writelines(data)

    def _random_ip(self):
        return random.choice([
            '192.168.1.52',
            '10.10.10.10',
            '22.22.2.222',
            '255.25.55.25',
            '16.2.33.45',
            '1.22.333.444'
        ])

    def _current_date(self):
        return '[{0} +0000]'.format(datetime.now().strftime('%d/%b/%Y:%H:%M:%S'))

    def _random_request(self):
        method = random.choice(['GET', 'PUT', 'POST', 'DELETE', 'HEAD'])
        protocol = 'HTTP/' + random.choice(['1.0', '1.1', '2'])

        page = '{0}.html'.format(random.choice(('edit', 'make', 'scrap', 'grab')))
        query_str = random.choice(['?randomise', ''])
        page += query_str

        sections = []
        for i in xrange(random.randint(1, 5)):
            sections.append(random.choice([chr(i) for i in xrange(65, 80)]))
        sections.append(page)

        url = '/'
        root_weight = 0.1
        if random.random() > root_weight:
            url += '/'.join(sections)

        return '"{0}"'.format(' '.join((method, url, protocol)))

    def _random_status(self):
        return str(random.choice([
            100, 101,
            200, 201, 206,
            301, 302, 304,
            401, 403, 404, 418, 451,
            500, 502, 503
        ]))


def main():
    import time
    import argparse

    parser = argparse.ArgumentParser(description='Apache http access log emulator')
    parser.add_argument('-p', '--path', help='path to write to [apache_log.txt]')
    parser.add_argument('-f', '--frequency', type=float, help='how often to write records, in s [3.3]')
    parser.add_argument('-c', '--count', type=int, help='max count of records to write [1000]')

    args = parser.parse_args()
    emulator = ApacheLogEmulator(args.path or 'apache_log.txt')

    while True:
        count = random.randint(0, args.count or 1000)
        print 'Generating {0} random http requests'.format(count)
        emulator.emulate(count)
        time.sleep(args.frequency or 3.3)


if __name__ == '__main__':
    main()
