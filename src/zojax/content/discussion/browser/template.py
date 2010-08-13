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
from email.Utils import formataddr

from zope import interface, component
from zope.component import getUtility, queryMultiAdapter, getAdapter
from zope.traversing.browser import absoluteURL
from zope.app.intid.interfaces import IIntIds

from zojax.mail.interfaces import IMailer
from zojax.content.type.interfaces import IContentViewView
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.content.discussion.interfaces import ICommentsNotification


class CommentNotificationMail(object):

    profile_url = None

    def update(self):
        super(CommentNotificationMail, self).update()

        content = self.context
        comment = self.context0
        self.comment = comment

        request = self.request

        principal = self.request.principal

        mailer = getUtility(IMailer)

        profile = IPersonalProfile(principal, None)
        if profile is not None and profile.email:
            author = profile.title
            self.author = author
            space = getattr(profile, 'space', None)
            if space is not None:
                self.profile_url = absoluteURL(space, request)
            self.addHeader(u'To', formataddr((author, profile.email),))
            self.addHeader(u'From', formataddr((author, mailer.email_from_address),))
        else:
            self.author = principal.title or principal.id

        view = queryMultiAdapter((content, request), IContentViewView)
        if view is not None:
            self.url = '%s/%s'%(absoluteURL(content, request), view.name)
        else:
            self.url = '%s/'%absoluteURL(content, request)

        self.content = comment.content
        self.subscription_id = getAdapter(comment.content, ICommentsNotification, 'comments').getSubscription(principal.id).id

    @property
    def subject(self):
        return u'New comment added to "%s"'%self.content.title

    @property
    def messageId(self):
        return u'<%s@zojax>'%getUtility(IIntIds).getId(self.comment)
