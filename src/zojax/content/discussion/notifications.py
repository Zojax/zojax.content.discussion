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
from zope import interface, component
from zope.component import getUtility, getAdapter
from zope.app.intid.interfaces import IIntIdAddedEvent

from zojax.subscription.interfaces import SubscriptionException
from zojax.subscription.interfaces import ISubscriptionDescription
from zojax.content.notifications.utils import sendNotification
from zojax.content.notifications.notification import Notification

from interfaces import _, ISimpleComment, IDiscussible
from interfaces import ICommentsNotification, ICommentsNotificationsAware


class CommentsNotification(Notification):
    component.adapts(ICommentsNotificationsAware)
    interface.implementsOnly(ICommentsNotification)

    type = u'comments'
    title = _(u'Recent comments')
    description = _(u'Recently added comments.')


class CommentsNotificationDescription(object):
    interface.implements(ISubscriptionDescription)

    type = u'comments'
    title = _(u'Recent comments')
    description = _(u'Recently added comments.')


@component.adapter(ISimpleComment, IIntIdAddedEvent)
def commentAdded(comment, ev):
    if ICommentsNotificationsAware.providedBy(comment.content):
        # send notification
        sendNotification('comments', comment.content, comment)


@component.adapter(IDiscussible, IIntIdAddedEvent)
def discussibleAdded(object, ev):
    # subscribe owner
    if ICommentsNotificationsAware.providedBy(object):
        notification = getAdapter(object, ICommentsNotification, 'comments')
        try:
            if not notification.isSubscribedInParents():
                notification.subscribe()
        except SubscriptionException:
            pass
