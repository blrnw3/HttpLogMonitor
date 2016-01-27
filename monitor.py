"""
:created: 15 Jan 2016
:author: bleerodgers blr@nw3weather.co.uk
"""

import time

from collections import defaultdict, Counter
from datetime import datetime, timedelta

from log_file_tailer import LogfileTailer
from w3c_parser import W3cParser


DATE_FORMAT = '%H:%M:%S %Y-%m-%d'


class Monitor(object):
    """
    Monitor HTTP traffic by consuming an actively written-to w3c-formatted HTTP access log
    """

    # Which fields to count the bandwidth and number of unique hits for
    fields_to_count = ('section', 'host', 'page', 'status')
    # Monitor latest traffic up to this long ago for hit threshold breaches
    hit_threshold_window = timedelta(seconds=120)
    # How many records to display for each field of interest
    top_n_to_display = 5

    def __init__(self, log_path, hit_threshold=2000):
        """
        Construct an HTTP access log monitor
        :param log_path: path to the w3c-formatted HTTP access log file
        :param hit_threshold: alert when hits in the last 2 mins exceeds this
        """
        self.hit_threshold = hit_threshold

        self.log_tailer = LogfileTailer(log_path=log_path, parser=W3cParser())

        self.records = None
        self.process_time = None
        self.hits_alert_active = False
        self.alerts = []

    def reset_stats(self):
        self.counts = defaultdict(Counter)
        self.bandwidths = defaultdict(Counter)
        self.totals = defaultdict(int)

    def update_stats(self, records):
        # Get counts for every field
        for record in records:
            for field in self.fields_to_count:
                self.counts[field][getattr(record, field)] += 1
                self.bandwidths[field][getattr(record, field)] += record.bytes
            self.totals['bytes'] += record.bytes

        self.totals['requests'] += len(records)

        # Get totals of unique requests
        for field, counter in self.counts.iteritems():
            self.totals[field] = len(counter)

    def update_recent_stats(self):
        # Update stats based on a recent timeframe. Requires considering all records,
        # not just the latest batch (though only those in the most recent window)
        self.recent_hits = 0
        now = datetime.now()
        i = len(self.records) - 1

        while i >= 0 and self.records[i].date > (now - self.hit_threshold_window):
            self.recent_hits += 1
            i -= 1

    def check_alerts(self):
        if self.recent_hits > self.hit_threshold and not self.hits_alert_active:
            self.alerts.append(Alert(self.hit_threshold, self.recent_hits))
            self.hits_alert_active = True
        elif self.recent_hits <= self.hit_threshold and self.hits_alert_active:
            self.alerts.append(Alert(self.hit_threshold, self.recent_hits))
            self.hits_alert_active = False

    def output_to_console(self):
        print '#################################'
        print 'Processed in {0:.3}s at {1}'.format(self.process_time,
                                                   datetime.now().strftime(DATE_FORMAT))
        if len(self.records) > 0:
            print 'Period: {0} - {1}'.format(
                self.records[0].date.strftime(DATE_FORMAT),
                self.records[-1].date.strftime(DATE_FORMAT)
            )
        print

        self.totals['pretty_bytes'] = pretty_bytes(self.totals['bytes'])
        print 'Hits: {requests}\tUsers: {host}\tData: {pretty_bytes}'.format(**self.totals)
        print 'Sections: {section}\tPages: {page}\t'.format(**self.totals)
        print 'Hits in last {0}s: {1}'.format(self.hit_threshold_window.seconds, self.recent_hits)
        print

        print 'No alerts to display' if not self.alerts else 'Alerts:'
        for alert in reversed(self.alerts):
            print alert
        print

        # TODO: use a table module to do this neater and more compactly
        for field, top_n_for_field in self.counts.iteritems():
            print 'Most hits by {0}'.format(field)
            for item, count in top_n_for_field.most_common(self.top_n_to_display):
                print '{0} ({1} hits, {2})'.format(
                    item, count, pretty_bytes(self.bandwidths[field][item])
                )
            print

        print '#################################'

    def process_new_records(self, records, reset):
        if reset:
            print 'Generating initial stats from w3c log'
            self.reset_stats()
            self.records = records
        else:
            print 'Updating stats with {0} new requests'.format(len(records))
            self.records.extend(records)

        self.update_stats(records)
        self.update_recent_stats()
        self.check_alerts()

    def run(self, tail=True, frequency=10):
        """
        Start the Monitor process, which runs continuously unless tail is False
        :param tail: loop continuously
        :param frequency: how often to get new records (only if tail is True)
        """
        print 'Parsing initial log file'
        while True:
            start = time.time()
            try:
                new_records, file_state = self.log_tailer.get_latest()
            except IOError as e:
                print e
                return

            parse_time = time.time()
            print 'Parsed in {0:.3}s'.format(parse_time - start)

            # Even if we have no new records, issue an update,
            #  since the time-dependent stats will have changed
            self.process_new_records(new_records, reset=(file_state == LogfileTailer.FILE_RESET))
            self.process_time = time.time() - parse_time
            self.output_to_console()
            if not tail:
                return
            time.sleep(frequency)


class Alert(object):
    """
    Container for traffic alerts: a counter exceeding and recovering from a threshold
    """

    def __init__(self, threshold, count):
        self.threshold = threshold
        self.count = count
        self.time = datetime.now()

    def __str__(self):
        message = ('WARN: High traffic generated an alert - hits: {value}, triggered at {time}'
                   if self.count > self.threshold else
                   'INFO: Recovered from high traffic at {time}, current hits: {value}')
        return message.format(
            value=self.count,
            time=self.time.strftime(DATE_FORMAT)
        )


def pretty_bytes(_bytes):
    """
    Pretty format a byte amount. Supports suffices up to TiB
    :param _bytes: number of bytes
    :return str: pretty-formatted byte string
    """
    format_str = '{0:.1f} {1}B'
    for SI_suffix in ('', 'Ki', 'Mi', 'Gi'):
        if _bytes < 1024:
            return format_str.format(_bytes, SI_suffix)
        _bytes /= 1024.0
    return format_str.format(_bytes, 'Ti')
