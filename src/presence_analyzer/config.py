# -*- encoding: utf-8 -*-
"""
Configuration file.
"""
import os.path

USERS_XML_REMOTE_FILE = 'http://sargo.bolt.stxnext.pl/users.xml'
USERS_XML_LOCAL_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data',
)
USERS_XML_LOCAL_FILE = os.path.join(
    USERS_XML_LOCAL_DIR, 'users.xml'
)
USERS_XML_TEST_FILE = os.path.join(
    USERS_XML_LOCAL_DIR, 'users_test.xml'
)
