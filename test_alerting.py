import unittest

from monitor import Monitor, Alert


class TestAlerting(unittest.TestCase):

    def setUp(self):
        self.threshold = 10
        self.monitor = Monitor(log_path=None, hit_threshold=self.threshold)

    def test_no_alerts_when_below_threshold(self):
        self.monitor.recent_hits = self.threshold
        for x in xrange(10):
            self.monitor.check_alerts()

        self.assertEquals(self.monitor.alerts, [])

    def test_single_alert_created_above_threshold(self):
        self.monitor.recent_hits = self.threshold + 1
        for x in xrange(10):
            self.monitor.check_alerts()
            self.monitor.recent_hits += 1

        self.assertEquals(len(self.monitor.alerts), 1)
        self.assertIsInstance(self.monitor.alerts[0], Alert)
        self.assertIn('WARN', str(self.monitor.alerts[0]))

    def test_two_alerts_above_then_below_threshold(self):
        self.monitor.recent_hits = self.threshold + 1
        self.monitor.check_alerts()
        self.monitor.recent_hits -= 1

        for x in xrange(10):
            self.monitor.check_alerts()

        self.assertEquals(len(self.monitor.alerts), 2)
        self.assertIn('WARN', str(self.monitor.alerts[0]))
        self.assertIn('INFO', str(self.monitor.alerts[1]))
