##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
import sys, types
from zope import interface
from zope.app.intid.interfaces import IIntIds
from zope.app.component.hooks import getSite, setSite
from zope.app.component.interfaces import ISite
from zope.app.publication.zopepublication import ZopePublication

from zojax.activity.interfaces import IActivity


def evolve(context):
    oldSite = getSite()
    root = context.connection.root()[ZopePublication.root_name]

    def findObjectsProviding(root):
        if ISite.providedBy(root):
            yield root

        values = getattr(root, 'values', None)
        if callable(values):
            for subobj in values():
                for match in findObjectsProviding(subobj):
                    yield match

    for site in findObjectsProviding(root):
        site._p_activate()

        setSite(site)

        sm = site.getSiteManager()

        list(sm.getUtility(IActivity).catalog.getIndexes())

    setSite(oldSite)
