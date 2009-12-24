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
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.traversing.api import getPath
from zope.app.component.hooks import getSite
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.cache.view import cache
from zojax.cache.keys import VisibleContext
from zojax.cache.timekey import TagTimeKey, each10minutes
from zojax.formatter.utils import getFormatter
from zojax.content.space.interfaces import ISpace, IWorkspace
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.content.discussion.catalog import getCatalog
from zojax.content.discussion.extension import CommentsTag


class RecentCommentsPortlet(object):

    comments = ()

    def __init__(self, context, request, manager, view):
        while not ISpace.providedBy(context):
            context = getattr(context, '__parent__', None)
            if context is None:
                break

        context = context or getSite()

        super(RecentCommentsPortlet, self).__init__(
            context, request, manager, view)

    def update(self):
        context = self.context
        if context is None:
            return

        self.comments = getCatalog().search(contexts=(context,))[:self.number]

        super(RecentCommentsPortlet, self).update()

    def listComments(self):
        auth = getUtility(IAuthentication)
        formatter = getFormatter(self.request, 'fancyDatetime', 'medium')

        comments = []
        for comment in self.comments:
            info = {'name': comment.__name__,
                    'title': comment.content.title,
                    'url': absoluteURL(comment.content, self.request),
                    'author': None,
                    'profile': None,
                    'date': comment.date,
                    'fomratteddate': formatter.format(comment.date)}

            try:
                principal = auth.getPrincipal(comment.author)
                profile = IPersonalProfile(principal)
                info['author'] = profile.title

                space = profile.space
                if space is not None:
                    info['profile'] = '%s/'%absoluteURL(space, self.request)

            except PrincipalLookupError:
                pass

            comments.append(info)

        return comments

    def isAvailable(self):
        return bool(self.comments)

    @cache('portlet.recentcomments',
           TagTimeKey(CommentsTag, each10minutes), VisibleContext)
    def updateAndRender(self):
        return super(RecentCommentsPortlet, self).updateAndRender()
