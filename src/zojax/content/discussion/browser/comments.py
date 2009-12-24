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
from zope.traversing.api import getPath
from zope.size.interfaces import ISized
from zope.security import checkPermission
from zope.component import getMultiAdapter

from zojax.cache.view import cache
from zojax.layout.interfaces import IPagelet
from zojax.content.type.interfaces import IDraftedContent

from zojax.content.discussion.cache import CommentsTag
from zojax.content.discussion.interfaces import \
    IContentDiscussion, IThreadedComment


def Modified(object, instance, *args, **kw):
    return {'modified': instance.discussion.modified,
            'context': getPath(instance.context),
            'allowPost': checkPermission('zojax.AddComment', instance.context)}


class Comments(object):

    def __init__(self, context, request):
        self.discussion = IContentDiscussion(context)

        super(Comments, self).__init__(context, request)

    def update(self):
        discussion = self.discussion

        level = 0
        comments = []

        def process(root, level, comments):
            if IThreadedComment.providedBy(root):
                for comment in root.children:
                    comments.append((level, comment))
                    if comment.children:
                        process(comment, level+1, comments)

        for comment in discussion.values():
            if IThreadedComment.providedBy(comment):
                if comment.parent is None:
                    comments.append((level, comment))
                    if comment.children:
                        process(comment, level+1, comments)
            else:
                comments.append((level, comment))

        self.comments = comments

    @cache('content.discussion', Modified, CommentsTag)
    def updateAndRender(self):
        return super(Comments, self).updateAndRender()


class CommentsPageElement(object):

    def update(self):
        discussion = IContentDiscussion(self.context)
        self.length = ISized(discussion).sizeForSorting()[1]
        self.hasComments = bool(len(discussion))

    def isAvailable(self):
        return not IDraftedContent.providedBy(self.context)
