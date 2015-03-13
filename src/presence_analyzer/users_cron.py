# -*- encoding: utf-8 -*-
"""
Python script for cron.
"""

import urllib2
# pylint: disable=relative-import
from config import (
    USERS_XML_REMOTE_FILE,
    USERS_XML_LOCAL_FILE
)


def get_users_xml():
    """
    Download actual users data XML.
    """
    f_remote = urllib2.urlopen(USERS_XML_REMOTE_FILE)
    data = f_remote.read()
    with open(USERS_XML_LOCAL_FILE, "w") as f_local:
        f_local.write(data)
    f_remote.close()
    return


if __name__ == '__main__':
    get_users_xml()
