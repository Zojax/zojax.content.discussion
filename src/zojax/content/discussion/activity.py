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
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds, IIntIdAddedEvent, IIntIdRemovedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zc.catalog.catalogindex import ValueIndex

from zojax.activity.record import ActivityRecord
from zojax.activity.catalog import Factory
from zojax.activity.interfaces import IActivity, IActivityRecordDescription
from zojax.content.activity.interfaces import IContentActivityRecord

from interfaces import _, IComment, ISimpleComment, ICommentActivityRecord


class CommentActivityRecord(ActivityRecord):
    interface.implements(ICommentActivityRecord, IContentActivityRecord)

    type = u'comment'
    verb = _('replied to')

    @property
    def comment(self):
        return getUtility(IIntIds).queryObject(self.commentId)


class CommentActivityRecordDescription(object):
    interface.implements(IActivityRecordDescription)

    title = _(u'Comment')
    description = _(u'Comment added to content object.')


class CommentIdIndex(Factory):
    def __call__(self):
        return ValueIndex('commentId')


@component.adapter(IComment, IIntIdAddedEvent)
def commentAddedHandler(comment, event):
    getUtility(IActivity).add(
        comment.content,
        CommentActivityRecord(commentId = getUtility(IIntIds).getId(comment)))


@component.adapter(IComment, IIntIdRemovedEvent)
def commentRemovedHandler(comment, event):
    activity = getUtility(IActivity)
    try:
        commentId = getUtility(IIntIds).getId(comment)
        for rid in activity.search(object=comment.content,
                                   noSecurityChecks=True,
                                   type={'any_of': ('comment',)},
                                   commentId={'any_of': (commentId,)}).uids:
            activity.remove(rid)
    except KeyError:
        pass
