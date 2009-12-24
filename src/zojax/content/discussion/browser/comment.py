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
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IAuthentication

from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.content.discussion.interfaces import IContentDiscussion


class CommentView(object):

    avatar = None
    author = u'Anonymous'
    url = ''

    def update(self):
        try:
            author = getUtility(IAuthentication).getPrincipal(
                self.context.author)
        except:
            author = None

        if author is not None:
            profile = IPersonalProfile(author)
            self.avatar = profile.avatarUrl(self.request)
            self.author = profile.title

            if profile.space is not None:
                self.url = absoluteURL(profile.space, self.request)
        else:
            self.avatar = u'%s/@@profile.avatar/0'%absoluteURL(
                getSite(), self.request)

        self.comment = self.context.comment

        content = self.context.content
        self.postsAllowed = (
            IContentDiscussion(content).status == 1 and
            checkPermission('zojax.AddComment', content))
