# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
from json import dumps
from functools import wraps
from datetime import datetime
import time
import threading
from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


CACHE_TIMESTAMP = {}
CACHE_DATA = {}


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


def memoize(period_of_validity):
    """
    Decorator - aplies cache for wrapped function.
    """
    lock = threading.Lock()

    def _memoize(cached_func):
        """
        First inner function for decorator.
        """

        def __memoize(*args, **kw):
            """
            Second inner function for decorator.
            """
            function_id = cached_func.__name__
            now = time.time()
            with lock:
                if (function_id in CACHE_TIMESTAMP) and \
                   (CACHE_TIMESTAMP[function_id] +
                   period_of_validity) > now:
                    return CACHE_DATA[function_id]

                result = cached_func(*args, **kw)
                CACHE_DATA[function_id] = result

                CACHE_TIMESTAMP[function_id] = now
                return result
        return __memoize
    return _memoize


@memoize(600)
def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


# pylint: disable=invalid-name
def group_start_end_times_by_weekday(items):
    """
    Returns a list with starts and ends for each weekday.
    """
    user_week = {
        i: {'start': [], 'end': []}
        for i in range(7)
    }
    for item in items:
        start = items[item]['start']
        end = items[item]['end']
        user_week[item.weekday()]['start'].append(
            seconds_since_midnight(start)
        )
        user_week[item.weekday()]['end'].append(
            seconds_since_midnight(end)
        )

    return user_week


def median(input_list):
    """
    Returns a median value from given list.
    """
    list_sorted = sorted(input_list)
    list_size = len(list_sorted)
    if not list_size:
        return 0.0
    else:
        if not (list_size % 2):
            idx1 = list_size / 2 - 1
            idx2 = idx1 + 1
            return (list_sorted[idx2] + list_sorted[idx1]) / 2.0
        else:
            idx = list_size / 2
            return float(list_sorted[idx])
