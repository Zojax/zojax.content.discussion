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
import cgi, pytz, time
from datetime import datetime

from z3c.form.interfaces import HIDDEN_MODE

from zope import interface
from zope.app.http.httpdate import build_http_date
from zope.event import notify
from zope.component import getUtility
from zope.security import checkPermission
from zope.interface.common.idatetime import ITZInfo
from zope.lifecycleevent import ObjectModifiedEvent
from zope.app.security.interfaces import IAuthentication

from zojax.cache.view import cache
from zojax.cache.keys import PrincipalAndContext
from zojax.cache.timekey import TimeKey, each30minutes
from zojax.cache.interfaces import DoNotCache

from zojax.layoutform import button, Fields, PageletForm
from zojax.layoutform.interfaces import ICancelButton
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.content.discussion.comment import Comment
from zojax.content.discussion.interfaces import _, IComment, IContentDiscussion
from zojax.content.discussion.utils import getVariablesForCookie, getAthorFromCookie


def PostCommentKey(object, instance, *args, **kw):
    instance.updateForms()
    if not instance.postsAllowed or \
            instance.request.has_key('discussion.buttons.post') or \
            (len(instance.forms) or len(instance.subforms)):
        raise DoNotCache()
    return ()


class PostCommentForm(PageletForm):

    ignoreContext = True
    label = _(u'Discuss')
    prefix = 'discussion.'

    def __init__(self, context, *args):
        super(PostCommentForm, self).__init__(context, *args)

        self.discussion = IContentDiscussion(context)
        self.postsAllowed = (self.discussion.status in [1, 4] and
                             checkPermission('zojax.AddComment', context))

        if self.isPrincipal():
            self.approved = True

    @property
    def fields(self):
        fields = Fields(IComment)
        fields['approved'].mode = HIDDEN_MODE
        fields['approved'].mode = HIDDEN_MODE
        if self.isPrincipal():
            fields = fields.omit('captcha', 'authorName')

        return fields

    def updateWidgets(self):
        super(PostCommentForm, self).updateWidgets()
        if not self.isPrincipal():
            # NOTE: get name from cookie
            self.widgets['authorName'].value = getAthorFromCookie(self.request)

    @button.buttonAndHandler(_('Post your comment'), name='post')
    def handlePost(self, action):
        request = self.request

        data, errors = self.extractData()
        if errors:
            IStatusMessage(request).add(
                _('Please fix indicated errors.'), 'warning')
        else:
            discussion = IContentDiscussion(self.context)

            commentText = cgi.escape(data['comment']).replace('\n', '<br />')

            comment = Comment(request.principal.id, commentText)
            comment.date = datetime.now(ITZInfo(request, pytz.utc))

            comment = discussion.add(comment)

            if 'authorName' in data:
                comment.authorName = data['authorName']

                # NOTE: set cookie for anon
                if not self.isPrincipal():
                    cookie_var = getVariablesForCookie(request)
                    expires = build_http_date(time.time() + 30000000) #347 days
                    request.response.setCookie(cookie_var['name'],
                                               data['authorName'],
                                               path=cookie_var['path'],
                                               expires=expires)

            msg = _('Your comment is awaiting moderation.')
            if self.isPrincipal():
                comment.approved = True
                msg = _('Comment has been added.')

            # NOTE: send modified event for original or new object
            notify(ObjectModifiedEvent(comment))

            IStatusMessage(request).add(msg)
            self.redirect('%s#comments'%request.getURL())

    def isAvailable(self):
        return self.postsAllowed

    def isPrincipal(self):
        try:
            principal = getUtility(IAuthentication).authenticate(self.request)
        except:
            principal = None

        return bool(principal)

    @cache('content.discussion.reply', PostCommentKey, PrincipalAndContext)
    def updateAndRender(self):
        return super(PostCommentForm, self).updateAndRender()


class PostComment(PageletForm):

    ignoreContext = True
    label = _(u'Reply to')
    replyto = None

    @property
    def fields(self):
        fields = Fields(IComment)
        fields['approved'].mode = HIDDEN_MODE
        fields['social_type'].mode = HIDDEN_MODE
        fields = fields.omit('social_avatar_url', 'social_name')

        if self.isPrincipal():
            fields = fields.omit('captcha', 'authorName')

        return fields

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

        if self.isPrincipal():
            self.approved = True

        super(PostComment, self).update()

    def updateWidgets(self):
        super(PostComment, self).updateWidgets()
        if not self.isPrincipal():
            # NOTE: get name from cookie
            self.widgets['authorName'].value = getAthorFromCookie(self.request)

    @button.buttonAndHandler(_('Reply to this comment'), name='post')
    def handlePost(self, action):
        request = self.request

        data, errors = self.extractData()
        if errors:
            IStatusMessage(request).add(
                _('Please fix indicated errors.'), 'warning')
        else:
            discussion = IContentDiscussion(self.context)

            commentText = cgi.escape(data['comment']).replace('\n', '<br />')

            comment = Comment(request.principal.id, commentText)
            comment.date = datetime.now(ITZInfo(request, pytz.utc))

            comment = discussion.add(comment)
            comment.setParent(self.replyto)

            if 'authorName' in data:
                comment.authorName = data['authorName']

                # NOTE: set cookie for anon
                if not self.isPrincipal():
                    cookie_var = getVariablesForCookie(request)
                    expires = build_http_date(time.time() + 30000000) #347 days
                    request.response.setCookie(cookie_var['name'],
                                               data['authorName'],
                                               path=cookie_var['path'],
                                               expires=expires)

            msg = _('Your comment is awaiting moderation.')
            if self.isPrincipal():
                comment.approved = True
                msg = _('Comment has been added.')

            # send modified event for original or new object
            notify(ObjectModifiedEvent(comment))

            IStatusMessage(request).add(msg)
            self.redirect('%s#comments'%request.getURL())

    def isPrincipal(self):
        try:
            principal = getUtility(IAuthentication).authenticate(self.request)
        except:
            principal = None

        return bool(principal)

    @button.buttonAndHandler(_('Cancel'), name='cancel', provides=ICancelButton)
    def handleCancel(self, action):
        self.redirect('.')

