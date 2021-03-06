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
    social_avatar = None
    social_name = None
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

        if author is not None or author == u'Unauthenticated User':
            if getattr(self.context, 'authorName'):
                self.author = self.context.authorName
                if 'social_avatar_url' in dir(self.context) and self.context.social_type:
                    self.social_avatar = self.context.social_avatar_url
                    if self.context.social_type==1:
                        self.social_name = 'Twitter'
                    elif self.context.social_type==2:
                        self.social_name = 'Facebook'

        self.comment = self.context.comment

        content = self.context.content
        self.postsAllowed = (
            IContentDiscussion(content).status in [1, 4] and
            checkPermission('zojax.AddComment', content))

    def isApproved(self):
        """ visible with the approval
        """

        content = self.context.content

        if IContentDiscussion(content).status == 4:
            return self.context.approved

        return True
