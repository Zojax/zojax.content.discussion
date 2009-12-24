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
import cgi, pytz
from datetime import datetime

from zope import interface
from zope.event import notify
from zope.security import checkPermission
from zope.interface.common.idatetime import ITZInfo

from zojax.cache.view import cache
from zojax.cache.keys import PrincipalAndContext
from zojax.cache.timekey import TimeKey, each30minutes
from zojax.cache.interfaces import DoNotCache

from zojax.layoutform import button, Fields, PageletForm
from zojax.layoutform.interfaces import ICancelButton
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.discussion.comment import Comment
from zojax.content.discussion.interfaces import _, IComment, IContentDiscussion


def PostComment(object, instance, *args, **kw):
    if not instance.postsAllowed or \
            instance.request.has_key('discussion.buttons.post'):
        raise DoNotCache()
    return ()


class PostCommentForm(PageletForm):

    fields = Fields(IComment)
    ignoreContext = True
    label = _(u'Discuss')
    prefix = 'discussion.'

    def __init__(self, context, *args):
        super(PostCommentForm, self).__init__(context, *args)

        self.discussion = IContentDiscussion(context)
        self.postsAllowed = (self.discussion.status == 1 and
                             checkPermission('zojax.AddComment', context))

    @button.buttonAndHandler(_('Post your comment'), name='post')
    def handlePost(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                _('Please fix indicated errors.'), 'warning')
        else:
            discussion = IContentDiscussion(self.context)

            commentText = cgi.escape(data['comment']).replace('\n', '<br />')

            comment = Comment(self.request.principal.id, commentText)
            comment.date = datetime.now(ITZInfo(self.request, pytz.utc))

            comment = discussion.add(comment)

            IStatusMessage(self.request).add(_('Comment has been added.'))
            self.redirect('%s#comments'%self.request.getURL())

    def isAvailable(self):
        return self.postsAllowed

    @cache('content.discussion.reply', PostComment, PrincipalAndContext)
    def updateAndRender(self):
        return super(PostCommentForm, self).updateAndRender()


class PostComment(PageletForm):

    fields = Fields(IComment)
    ignoreContext = True
    label = _(u'Reply to')
    replyto = None

    def update(self):
        self.discussion = IContentDiscussion(self.context, None)
        if self.discussion is None or self.discussion.status != 1:
            self.redirect('.')
            return

        if 'replyto' in self.request:
            self.replyto = self.discussion.get(self.request.get('replyto', ''))

        if self.replyto is None:
            self.redirect('.')
            return

        super(PostComment, self).update()

    @button.buttonAndHandler(_('Reply to this comment'), name='post')
    def handlePost(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                _('Please fix indicated errors.'), 'warning')
        else:
            discussion = IContentDiscussion(self.context)

            commentText = cgi.escape(data['comment']).replace('\n', '<br />')

            comment = Comment(self.request.principal.id, commentText)
            comment.date = datetime.now(ITZInfo(self.request, pytz.utc))

            comment = discussion.add(comment)
            comment.setParent(self.replyto)

            IStatusMessage(self.request).add(_('Comment has been added.'))
            self.redirect('%s#comments'%self.request.getURL())

    @button.buttonAndHandler(_('Cancel'), name='cancel', provides=ICancelButton)
    def handleCancel(self, action):
        self.redirect('.')
