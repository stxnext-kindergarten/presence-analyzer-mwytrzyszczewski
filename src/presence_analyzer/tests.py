from __future__ import unicode_literals
# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
import os.path
import json
import datetime
import unittest


from presence_analyzer import (
    main,
    utils
)


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)

TEST_USER_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up an environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'USERS_XML_LOCAL_FILE': TEST_USER_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        assert resp.headers['Location'].endswith('presence_weekday')

    def test_api_users(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)
        self.assertDictEqual(data[0], {'user_id': 10, 'name': 'User 10'})

    def test_api_users_data(self):
        """
        Test users listing with personal data.
        """
        resp = self.client.get('/api/v1/users_data')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')

        data = json.loads(resp.data)
        self.assertEqual(len(data), 3)

        expected_data = [
            {
                'user_id': '141',
                'name': 'Adam P.',
                'avatar': 'https://intranet.stxnext.pl:443'
                          '/api/images/users/141',
            },
            {
                'user_id': '176',
                'name': 'Adrian K.',
                'avatar': 'https://intranet.stxnext.pl:443'
                          '/api/images/users/176',
            },
            {
                'user_id': '170',
                'name': 'Agata J.',
                'avatar': 'https://intranet.stxnext.pl:443'
                          '/api/images/users/170',
            },
        ]
        self.assertListEqual(json.loads(resp.data), expected_data)

    def test_mean_time_weekday_view(self):
        """
        Test mean time weekday view.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/10000')
        self.assertEqual(json.loads(resp.data), 'no_data')

        resp = self.client.get('/api/v1/mean_time_weekday/10')
        self.assertEqual(resp.status_code, 200)

        resp_data = json.loads(resp.data)
        expected_data = [
            ["Mon", 0],
            ["Tue", 30047.0],
            ["Wed", 24465.0],
            ["Thu", 23705.0],
            ["Fri", 0],
            ["Sat", 0],
            ["Sun", 0]
        ]

        self.assertEqual(resp_data, expected_data)

    def test_presence_weekday_view(self):
        """
        Test presence weekday view.
        """
        resp = self.client.get('/api/v1/presence_weekday/10000')
        self.assertEqual(json.loads(resp.data), 'no_data')

        resp = self.client.get('/api/v1/presence_weekday/10')
        self.assertEqual(resp.status_code, 200)

        resp_data = json.loads(resp.data)
        expected_data = [
            ["Weekday", "Presence (s)"],
            ["Mon", 0],
            ["Tue", 30047],
            ["Wed", 24465],
            ["Thu", 23705],
            ["Fri", 0],
            ["Sat", 0],
            ["Sun", 0]
        ]

        self.assertEqual(resp_data, expected_data)

    def test_presence_start_end_view(self):
        """
        Test mean starting and ending time.
        """
        resp = self.client.get('/api/v1/presence_start_end/10000')
        self.assertEqual(json.loads(resp.data), 'no_data')
        resp = self.client.get('/api/v1/presence_start_end/10')
        self.assertEqual(resp.status_code, 200)
        resp_data = json.loads(resp.data)
        expected_data = [
            ['Mon', 0, 0],
            ['Tue', 34745.0, 64792.0],
            ['Wed', 33592.0, 58057.0],
            ['Thu', 38926.0, 62631.0],
            ['Fri', 0, 0],
            ['Sat', 0, 0],
            ['Sun', 0, 0]
        ]

        self.assertEqual(resp_data, expected_data)

    def test_page_to_display(self):
        """
        Test showing chosen page, including "error 404".
        """
        resp = self.client.get('/mean_time_weekday')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/presence_start_end')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/presence_weekday')
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/nonexistingpage')
        self.assertEqual(resp.status_code, 404)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11])
        sample_date = datetime.date(2013, 9, 10)
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(
            data[10][sample_date]['start'],
            datetime.time(9, 39, 5)
        )

    def test_group_by_weekday(self):
        """
        Test groups presence entries by weekday.
        """
        sample_week = {
            datetime.date(2015, 2, 2): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 3): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 4): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 5): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 6): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 0, 0)
            },
            datetime.date(2015, 2, 7): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(12, 0, 0)
            },
            datetime.date(2015, 2, 8): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(10, 0, 0)
            },
        }

        result = utils.group_by_weekday(sample_week)
        self.assertIsInstance(result, list)
        self.assertItemsEqual(
            result,
            [[28800], [28800], [28800], [28800], [28800], [10800], [3600]]
        )

    def test_seconds_since_midnight(self):
        """
        Test seconds since midnight.
        """
        result = utils.seconds_since_midnight(datetime.time(0, 0, 0))
        self.assertEqual(result, 0)
        result = utils.seconds_since_midnight(datetime.time(12, 0, 0))
        self.assertEqual(result, 43200)
        result = utils.seconds_since_midnight(datetime.time(23, 59, 59))
        self.assertEqual(result, 86399)

    def test_interval(self):
        """
        Test calculating inverval in seconds between two datetime.time objects.
        """
        time_start = datetime.time(0, 0, 0)
        time_end = datetime.time(0, 0, 0)
        result = utils.interval(time_start, time_end)
        self.assertEqual(result, 0)

        time_start = datetime.time(0, 0, 0)
        time_end = datetime.time(0, 0, 1)
        result = utils.interval(time_start, time_end)
        self.assertEqual(result, 1)

        time_start = datetime.time(0, 0, 1)
        time_end = datetime.time(0, 0, 0)
        result = utils.interval(time_start, time_end)
        self.assertEqual(result, -1)

    def test_mean(self):
        """
        Test calculating arithmetic mean.
        """
        items = []
        result = utils.mean(items)
        self.assertEqual(result, 0)

        items = [1, 2, 3]
        result = utils.mean(items)
        self.assertEqual(result, 2.0)

        items = [-1, 1]
        result = utils.mean(items)
        self.assertEqual(result, 0.0)

        items = [-3, -2, -1]
        result = utils.mean(items)
        self.assertEqual(result, -2.0)

        items = [1.8, 2.1, 3.7, 4.3]
        result = utils.mean(items)
        self.assertEqual(result, 2.975)

# pylint: disable=import-error, no-name-in-module
    def test_group_start_end_times_by_weekday(self):
        """
        Test creating list starting and ending work time for specyfic user.
        """
        some_data = utils.get_data()
        expected_data = {
            0: {'start': [], 'end': []},
            1: {'start': [34745], 'end': [64792]},
            2: {'start': [33592], 'end': [58057]},
            3: {'start': [38926], 'end': [62631]},
            4: {'start': [], 'end': []},
            5: {'start': [], 'end': []},
            6: {'start': [], 'end': []}
        }

        result = utils.group_start_end_times_by_weekday(some_data[10])
        self.assertIsInstance(result, dict)
        self.assertItemsEqual(result, expected_data)
# pylint: enable=import-error, no-name-in-module


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
