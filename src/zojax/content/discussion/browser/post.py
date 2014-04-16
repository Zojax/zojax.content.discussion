#
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
#
"""

$Id$
"""
import cgi
import pytz
import time
from datetime import datetime

from z3c.form.interfaces import HIDDEN_MODE

from zope.app.http.httpdate import build_http_date
from zope.app.security.interfaces import IAuthentication
from zope.event import notify
from zope.component import getUtility
from zope.security import checkPermission
from zope.interface.common.idatetime import ITZInfo
from zope.lifecycleevent import ObjectModifiedEvent
from zope.traversing.api import getPath

from zojax.cache.view import cache
from zojax.cache.interfaces import DoNotCache

from zojax.layoutform import button, Fields, PageletForm
from zojax.layoutform.interfaces import ICancelButton
from zojax.resourcepackage.library import include
from zojax.statusmessage.interfaces import IStatusMessage

from ..comment import Comment
from ..interfaces import _, IComment, IContentDiscussion, ISocialComment, \
    ITwitterCommentingConfig, IFacebookCommentingConfig
from ..utils import getVariablesForCookie, getAthorFromCookie


def PostCommentKey(object, instance, *args, **kw):
    instance.updateForms()
    if not instance.postsAllowed or \
            instance.request.has_key('discussion.buttons.post') or \
            (len(instance.forms) or len(instance.subforms)):
        raise DoNotCache()
    return ()


def PrincipalAndContext(object, instance, *args, **kw):
    return {'principal': instance.request.principal.id,
            'context': getPath(instance.context),
            'allowPost': checkPermission('zojax.AddComment', instance.context),
            'facebook_id': instance.request.get('facebook_id', ''),
            'screen_name': instance.request.get('screen_name', '')}


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
        if self.networks and self.discussion.status == 4:
            fields = Fields(ISocialComment).omit(
                'social_avatar_url', 'social_name')
            fields['approved'].mode = HIDDEN_MODE
            fields['social_type'].mode = HIDDEN_MODE
            fields['facebook_id'].mode = HIDDEN_MODE
            fields['twitter_id'].mode = HIDDEN_MODE
            fields['captcha'].field.title = u'Caption'
            if self.isPrincipal():
                fields = fields.omit(
                    'captcha', 'authorName', 'facebook_id', 'social_type', 'twitter_id')
        else:
            fields = Fields(IComment)
            fields['approved'].mode = HIDDEN_MODE
            if self.isPrincipal():
                fields = fields.omit('captcha', 'authorName')

        return fields

    def updateWidgets(self):
        super(PostCommentForm, self).updateWidgets()

        include('js-social-logins')

        if not self.isPrincipal() and getAthorFromCookie(self.request):
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

            tab = 'guest'
            # TODO: check configlets
            if 'social_type' in data and data['social_type']:
                comment.social_type = data['social_type']
                comment.social_name = comment.authorName
                if comment.social_type == 1:
                    comment.twitter_id = self.request.cookies['screen_name']
                    comment.social_avatar_url = getUtility(
                        ITwitterCommentingConfig).avatarUrl + comment.twitter_id
                    tab = 'twitter'
                elif comment.social_type == 2:
                    comment.facebook_id = self.request.cookies['facebook_id']
                    comment.social_avatar_url = getUtility(
                        IFacebookCommentingConfig).avatarUrl + comment.facebook_id + '/picture'
                    tab = 'facebook'
            else:
                # NOTE: set cookie for anon
                if not self.isPrincipal():
                    cookie_var = getVariablesForCookie(request)
                    # 347 days
                    expires = build_http_date(time.time() + 30000000)
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
            # self.redirect('%s#comments'%request.getURL())
            # self.redirect('%s?tab=%s#comment-form' % (request.getURL(), tab))
            self.redirect('%s#%s' % (request.getURL(), tab))

    def update(self):
        super(PostCommentForm, self).update()

        request = self.request
        self.twi = None
        self.fb = None

        # Twitter
        # screen_name, tw_name, user_id
        if request.has_key('screen_name') and request.has_key('tw_name'):
            avatar = "%s%s" % (
                getUtility(ITwitterCommentingConfig).avatarUrl, request['screen_name'])
            self.twi = dict(avatar=avatar, name=request['tw_name'])

        # Facebook
        # facebook_id, fb_author
        if request.has_key('facebook_id') and request.has_key('fb_author'):
            avatar = "%s%s/picture" % (
                getUtility(IFacebookCommentingConfig).avatarUrl, request['facebook_id'])
            self.fb = dict(avatar=avatar, name=request['fb_author'])

    def isAvailable(self):
        return self.postsAllowed

    def isPrincipal(self):
        try:
            principal = getUtility(IAuthentication).authenticate(self.request)
        except:
            principal = None

        return bool(principal)

    @property
    def networks(self):
        result = []

        if getUtility(ITwitterCommentingConfig).isVisible:
            result.append('twitter')

        if getUtility(IFacebookCommentingConfig).isVisible:
            result.append('facebook')

        return result

    @property
    def action(self):
        """See interfaces.IInputForm"""
        return self.request.getURL() + '#comment-form'

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
        if 'social_type' in fields:
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
                    # 347 days
                    expires = build_http_date(time.time() + 30000000)
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
            self.redirect('%s#comments' % request.getURL())

    def isPrincipal(self):
        try:
            principal = getUtility(IAuthentication).authenticate(self.request)
        except:
            principal = None

        return bool(principal)

    @button.buttonAndHandler(_('Cancel'), name='cancel', provides=ICancelButton)
    def handleCancel(self, action):
        self.redirect('.')
