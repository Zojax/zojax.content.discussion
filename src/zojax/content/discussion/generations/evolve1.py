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
from install import evolve
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import getSite, setSite
from zope.app.generations.utility import findObjectsProviding
from zope.app.publication.zopepublication import ZopePublication

from zojax.content.discussion.catalog import getCatalog

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

        catalog = getCatalog()

        for comment in catalog.searchResults(
                           date = {'any_of': tuple(catalog['date'].values())},):
            try:
                comment.approved = True

            except KeyError:
                print 'approved attribute is not added to the comment'

    setSite(oldSite)
