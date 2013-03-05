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
from zope.app.container.interfaces import IObjectAddedEvent

from zojax.subscription.interfaces import SubscriptionException
from zojax.subscription.interfaces import ISubscriptionDescription
from zojax.content.notifications.utils import sendNotification
from zojax.content.notifications.notification import Notification

from interfaces import _, ISimpleComment, IDiscussible, IContentDiscussionConfig
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


@component.adapter(ISimpleComment, IObjectAddedEvent)
def commentAdded(comment, ev):
    """ sends emails when the comment is created """
    if not ICommentsNotificationsAware.providedBy(comment.content):
        return

    notification = getAdapter(comment.content, ICommentsNotification, 'comments')
    configlet = getUtility(IContentDiscussionConfig)

    if comment.isAvailable() and configlet.notificationsReceivers == 1:
        # check subscribe for current user
        try:
            if not notification.isSubscribedInParents():
                notification.subscribe()
        except SubscriptionException:
            pass

        # send notification
        sendNotification('comments', comment.content, comment)
    else:
        if configlet.notifyUsers:
            # subscribe
            for principal in configlet.notifyUsers:
                try:
                    if not notification.isSubscribedInParents(comment.content, principal):
                        notification.subscribe(principal)
                except SubscriptionException:
                    pass

            # send notification
            sendNotification('comments', comment.content, comment, principal={'any_of': configlet.notifyUsers})

            ## unsubscribe
            #for principal in configlet.notifyUsers:
            #    notification.unsubscribe(principal)


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
