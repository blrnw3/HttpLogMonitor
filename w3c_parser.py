import re

from collections import namedtuple
from datetime import datetime


Record = namedtuple('Record', 'host ident user date method section protocol status bytes page')

month_num = dict(Jan=1, Feb=2, Mar=3, Apr=4, May=5, Jun=6, Jul=7, Aug=8, Sep=9,
                 Oct=10, Nov=11, Dec=12)

class W3cParser(object):
    """
    Parses records from a w3c-formatted http logfile
    """

    # Captures all desired groups. Quicker than a generic tokenizer like '[\["](.*?)[\]"]|(\S+)'
    LOG_RECORD_REGEX = re.compile('([(\d\.)]+) (.*?) (.*?) \[(.*?)\] "(.*?)" (\d{3}) (\d+|-)')

    # W3C format has these fields, in this order.
    log_fields = ('host', 'ident', 'user', 'date', 'request', 'status', 'bytes')
    log_field_map = {field: i for i, field in enumerate(log_fields)}

    def parse_line(self, raw_record):
        """
        Parses useful data from a line of a w3c http log file
        :param raw_record str: line of the log to parse
        :return: Record object with all relevant data
        """
        # Merge the matched groups since they never overlap
        raw_fields = self.LOG_RECORD_REGEX.match(raw_record).groups()
        record = {}
        for i, field in enumerate(self.log_fields):
            record[field] = raw_fields[i]

        record['date'] = self._parse_date(record['date'])
        record['bytes'] = self._parse_bytes(record['bytes'])

        method, page, section, protocol = self._parse_request(record['request'])
        del record['request']
        record.update(method=method, page=page, section=section, protocol=protocol)

        return Record(**record)

    def _parse_request(self, request_str):
        method, page, protocol = request_str.split()
        sections = page.split('/')
        # One slash signifies the page is at the root
        section = sections[1] if len(sections) > 2 else 'root'
        # Strip query params from page
        page = page.split('?')[0]
        return method, page, section, protocol

    def _parse_date(self, date_str):
        # Ignore the TZ since native lib can't handle it.
        # TODO: Ideally we'd use a library for extracting this
        # Not using datetime.strptime as it was found to be very slow (x10 vs below))
        # return datetime.strptime(date_str.split()[0], '%d/%b/%Y:%H:%M:%S')
        # The date_str is fixed width so we can parse by slicing
        # e.g. 14/Jan/2016:13:50:24 +0000
        day = int(date_str[0:2])
        month = month_num[date_str[3:6]]
        year = int(date_str[7:11])
        hour = int(date_str[12:14])
        minute = int(date_str[15:17])
        second = int(date_str[18:20])
        return datetime(year, month, day, hour, minute, second)

    def _parse_bytes(self, byte_str):
        return 0 if byte_str == '-' else int(byte_str)