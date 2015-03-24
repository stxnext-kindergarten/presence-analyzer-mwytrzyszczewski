# -*- coding: utf-8 -*-
"""
Defines views.
"""

# pylint: disable=import-error, no-name-in-module
import calendar
from flask import redirect
from flask.ext.mako import render_template, exceptions
from lxml import etree

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    mean,
    group_by_weekday,
    group_start_end_times_by_weekday,
    median
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
    options = [
        ['presence_weekday', 'Presence by weekday'],
        ['mean_time_weekday', 'Presence mean time'],
        ['presence_start_end', 'Presence start-end'],
        ['median_weekday', 'Presence median time']
    ]
    try:
        return render_template(chosen_template+'.html', options=options)
    except exceptions.TemplateLookupException:
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


@app.route('/api/v1/users_data', methods=['GET'])
@jsonify
def users_view_data():
    """
    Users listing for dropdown.
    """
    with open(app.config['USERS_XML_LOCAL_FILE'], 'r') as f_xml:
        tree = etree.parse(f_xml)    # pylint: disable=no-member
    data_server = tree.find('server')
    url_prefix = '{0}://{1}:{2}'.format(
        data_server.find('protocol').text,
        data_server.find('host').text,
        data_server.find('port').text
    )
    result = [
        {
            'user_id': person.get('id'),
            'name': person.findtext('name'),
            'avatar': '{0}{1}'.format(url_prefix, person.findtext('avatar')),
        }
        for person in tree.findall('./users/user')
    ]
    return result


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return 'no_data'

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
        return 'no_data'

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
        return 'no_data'

    week = group_start_end_times_by_weekday(data[user_id])

    result = []
    for day in week:
        starts = mean(week[day]['start'])
        ends = mean(week[day]['end'])
        result.append([calendar.day_abbr[day], starts, ends])

    return result


@app.route('/api/v1/median_weekday/<int:user_id>', methods=['GET'])
@jsonify
def median_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return 'no_data'

    weekdays = group_by_weekday(data[user_id])
    result = [
        (calendar.day_abbr[weekday], median(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]
    return result
