"""
:created: 15 Jan 2016
:author: bleerodgers blr@nw3weather.co.uk
"""

import os


class LogfileTailer(object):
    """
    Efficient handling of tail-like access to a rotating log file
    """

    # Each time we check the file, it can be in one of these states
    FILE_UNCHANGED = 0  # No changes since last read
    FILE_RESET = 1  # File is changed completely (rotated)
    FILE_UPDATE = 2  # File has new records which need parsing

    def __init__(self, log_path, parser=None):
        """
        :param log_path: path to the rotating log file
        :param parser: line parser with a parse_line method for extracting data
        """
        self.log_path = log_path
        self.parser = parser

        self.file_size = None

    def get_latest(self):
        """
        Get all records since the last request, or all records if the file contains new data
        And return the file state (unchanged, reset, updated)
        :return: tuple (new_records, file_state)
        """
        file_state = self._get_file_state()
        records = []

        if file_state != self.FILE_UNCHANGED:
            records = self._process(seek_to_last=(file_state == self.FILE_UPDATE))

        return records, file_state

    def _get_file_state(self):
        if not os.path.exists(self.log_path):
            raise IOError('Path {0} is not a valid file'.format(self.log_path))

        new_file_size = os.path.getsize(self.log_path)
        if new_file_size == self.file_size:
            return self.FILE_UNCHANGED

        if self.file_size is None or new_file_size < self.file_size:
            return self.FILE_RESET
        else:
            return self.FILE_UPDATE

    def _process(self, seek_to_last=False):
        records = []
        with open(self.log_path, 'r') as f:
            if seek_to_last:
                f.seek(self.file_size)
            for line in f:
                try:
                    records.append(
                        self.parser.parse_line(line) if self.parser else line
                    )
                except Exception as e:
                    # Skip dodgy lines. TODO: Could write them to a log maybe
                    print 'PARSER WARN: faulty line [{0}] skipped: {1}'.format(line, e)
            self.file_size = f.tell()  # Accurate latest file size based on what we read
        return records
