##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""

from zope.app.component.hooks import getSite
from zope.traversing.browser import absoluteURL

try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5


def getVariablesForCookie(request=None):
    """ returns dict with variables for cookie
    """
    cookie_path = '/'

    portalurl = absoluteURL(getSite(), request)
    cookie_name = "%s%s"%('__zojax_comment_author_', md5(portalurl).hexdigest())

    return dict(name=cookie_name, path=cookie_path)


def getAthorFromCookie(request=None):
    """ returns Athor from cookie
    """
    if not request:
        return '___'

    cookie_name = getVariablesForCookie(request)['name']

    if request.has_key(cookie_name):
        return request[cookie_name]

    return '___'
