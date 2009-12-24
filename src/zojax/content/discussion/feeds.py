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
import time, rfc822
from zope import interface, component
from zope.component import getUtility
from zope.traversing.browser import absoluteURL
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.content.feeds.rss2 import RSS2Feed
from zojax.content.space.interfaces import ISpace
from zojax.content.discussion.catalog import getCatalog
from zojax.principal.profile.interfaces import IPersonalProfile

from interfaces import _, ICommentsRSSFeed, IDiscussible, IContentDiscussion


class CommentsFeed(RSS2Feed):
    component.adapts(ISpace)
    interface.implementsOnly(ICommentsRSSFeed)

    name = u'comments'
    title = _(u'Recent comments')
    description = _(u'Recently added comments.')

    def items(self):
        request = self.request
        auth = getUtility(IAuthentication)
        comments = getCatalog().search(contexts=(self.context,))[:15]

        for comment in comments:
            url = absoluteURL(comment.content, request)

            info = {
                'link': '%s/'%url,
                'description': comment.comment,
                'guid': '%s/#comments%s'%(url, comment.__name__),
                'pubDate': rfc822.formatdate(time.mktime(comment.date.timetuple())),
                'isPermaLink': True}

            author = u'Unknown'
            try:
                principal = auth.getPrincipal(comment.author)
                profile = IPersonalProfile(principal)
                author = profile.title
                info['author'] = u'%s (%s)'%(profile.email, author)
            except PrincipalLookupError:
                pass

            info['title'] = _(u'by ${author} on ${content}',
                              mapping={'author': author, 'content': comment.content.title})
            yield info


class ContentCommentsFeed(RSS2Feed):
    component.adapts(IDiscussible)
    interface.implementsOnly(ICommentsRSSFeed)

    name = u'comments'
    title = _(u'Content comments')
    description = _(u'Recent comments for this content item.')

    def items(self):
        request = self.request
        auth = getUtility(IAuthentication)
        discussion = IContentDiscussion(self.context)

        for idx in discussion:
            comment = discussion[idx]
            url = absoluteURL(comment.content, request)

            info = {
                'link': '%s/'%url,
                'description': comment.comment,
                'guid': '%s/#comments%s'%(url, comment.__name__),
                'pubDate': rfc822.formatdate(time.mktime(comment.date.timetuple())),
                'isPermaLink': True}

            author = u'Unknown'
            try:
                principal = auth.getPrincipal(comment.author)
                profile = IPersonalProfile(principal)
                author = profile.title
                info['author'] = u'%s (%s)'%(profile.email, author)
            except PrincipalLookupError:
                pass

            info['title'] = _('by ${author}', mapping={'author': author})
            yield info
