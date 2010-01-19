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
from zope import interface, schema
from zope.i18nmessageid import MessageFactory
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zojax.widget.radio.field import RadioChoice
from zojax.content.feeds.interfaces import IRSS2Feed
from zojax.content.discussion.vocabulary import commentPolicyVocabulary, \
                                                postCommentPositionVocabulary, \
                                                commentsOrderVocabulary
from zojax.content.notifications.interfaces import IContentNotification

_ = MessageFactory('zojax.content.discussion')


class ICommentsNotificationsAware(interface.Interface):
    """ marker interface for notifications aware content """


class IDiscussible(interface.Interface):
    """Content possibly discussible"""


class IOpenDiscussible(IDiscussible):
    """Content with open discussion by default."""


class IComment(interface.Interface):
    """Discussion comment"""

    author = interface.Attribute('Author')

    date = interface.Attribute('Comment date')

    title = interface.Attribute('Title')

    comment = schema.Text(
        title = _(u'Comment'),
        required = True)

    content = interface.Attribute('Content')


class ISimpleComment(IComment):
    """ simple comment """


class IThreadedComment(interface.Interface):
    """ threaded comment """

    parent = interface.Attribute('Comment parent')

    children = interface.Attribute('List of children comments')


class IContentDiscussion(interface.Interface):
    """Content discussion extension"""

    status = RadioChoice(
        title = _(u'Content discussion'),
        description = _('Select comment policy for this item.'),
        vocabulary = commentPolicyVocabulary,
        default = 3,
        required = True)

    lastid = interface.Attribute('Last id')
    modified = interface.Attribute('Last modified')

    def add(comment):
        """ add comment """


class ICommentEvent(IObjectEvent):
    """ comment event """

    comment = interface.Attribute('Comment')


class ICommentAddedEvent(ICommentEvent):
    """ comment added event for content object """


class ICommentRemovedEvent(ICommentEvent):
    """ comment removed event for content object """


class CommentEvent(ObjectEvent):

    def __init__(self, object, comment):
        super(CommentEvent, self).__init__(object)

        self.comment = comment


class CommentAddedEvent(CommentEvent):
    interface.implements(ICommentAddedEvent)


class CommentRemovedEvent(CommentEvent):
    interface.implements(ICommentRemovedEvent)


class IContentDiscussionAware(interface.Interface):
    """Content discussion aware"""


class ICommentsCatalog(interface.Interface):
    """ commments catalog """


class IRecentCommentsPortlet(interface.Interface):
    """ recent comments portlet """

    number = schema.Int(
        title = _(u'Number of comments'),
        description = _(u'Number of comments to display'),
        default = 10,
        required = True)


class ICommentsRSSFeed(IRSS2Feed):
    """ comments rss feed """


class ICommentsNotification(IContentNotification):
    """ comments notification """


class ICommentActivityRecord(interface.Interface):
    """ comment activity record """

    comment = interface.Attribute('Comment object')
    commentId = interface.Attribute('Comment int id')


class IContentDiscussionConfig(interface.Interface):
    """ config """

    postCommentPosition = RadioChoice(
        title = _(u'Post comment form position'),
        description = _('Select post comment form position'),
        vocabulary = postCommentPositionVocabulary,
        default = 1,
        required = True)

    commentsOrder = RadioChoice(
        title = _(u'Comments order'),
        description = _('Select order in which to dispay comments.'),
        vocabulary = commentsOrderVocabulary,
        default = 1,
        required = True)


class IContentDiscussionConfiglet(IContentDiscussionConfig):
    """ configlet """
