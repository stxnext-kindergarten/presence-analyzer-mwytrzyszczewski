# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
# p y lint: disable=import-error, no-name-in-module
from flask import Flask
from flask.ext.mako import MakoTemplates

app = Flask(__name__)  # pylint: disable=invalid-name
mako = MakoTemplates(app)
