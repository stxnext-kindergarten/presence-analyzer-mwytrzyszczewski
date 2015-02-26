# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, abort, render_template
import jinja2

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_start_end_times_by_weekday
)


import logging
log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.errorhandler(404)
def page_not_found(error):
    """
    Shows "Error 404 page not found" message.
    """
    return render_template('error.html', error=error), 404


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/presence_weekday')


@app.route('/<chosen_template>')
def page_to_display(chosen_template):
    """
    Shows page with chosen option.
    """
    options = {
        'presence_weekday': 'Presence by weekday',
        'mean_time_weekday': 'Presence mean time',
        'presence_start_end': 'Presence start-end'
    }
    try:
        return render_template(chosen_template+'.html', options=options)
    except jinja2.TemplateNotFound:
        return render_template('error.html', error='Page not found.'), 404


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns mean start time and mean end time.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        abort(404)

    week = group_start_end_times_by_weekday(data[user_id])

    result = []
    for day in week:
        starts = mean(week[day]['start'])
        ends = mean(week[day]['end'])
        result.append([calendar.day_abbr[day], starts, ends])

    return result
