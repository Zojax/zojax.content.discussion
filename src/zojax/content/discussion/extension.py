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
import time
from BTrees.Length import Length
from rwproperty import getproperty, setproperty

from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.app.intid.interfaces import IIntIdAddedEvent, IIntIdRemovedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.app.container.interfaces import \
    IObjectAddedEvent, IObjectRemovedEvent, IContainerModifiedEvent

from zojax.cache.tag import ContextTag
from zojax.extensions.container import ContentContainerExtension

from catalog import getCatalog

from interfaces import CommentAddedEvent, CommentRemovedEvent
from interfaces import IComment, IDiscussible, IOpenDiscussible
from interfaces import IContentDiscussion, IContentDiscussionAware
from notifications import discussibleAdded


CommentsTag = ContextTag('zojax.discussion')


class ContentDiscussionExtension(ContentContainerExtension):
    interface.implements(IContentDiscussion)

    @getproperty
    def status(self):
        return getattr(self.data, 'status', 3)

    @setproperty
    def status(self, value):
        context = removeAllProxies(self.context)

        roleper = IRolePermissionManager(context)
        if value == 4:
            roleper.grantPermissionToRole('zojax.AddComment', 'zope.Anonymous')
        else:
            roleper.denyPermissionToRole('zojax.AddComment', 'zope.Anonymous')

        if value == 3:
            if IContentDiscussionAware.providedBy(context):
                interface.noLongerProvides(context, IContentDiscussionAware)
        else:
            if not IContentDiscussionAware.providedBy(context):
                interface.alsoProvides(context, IContentDiscussionAware)
                discussibleAdded(context, None)

        self.data.status = value

    @property
    def lastid(self):
        lastid = getattr(self.data, 'lastid', None)
        if lastid is None:
            idx = 1

            name = '%0.3d'%idx
            while name in self:
                idx = idx + 1
                name = '%0.3d'%idx

            lastid = Length(idx)
            self.data.lastid = lastid

        return lastid

    @getproperty
    def modified(self):
        modified = getattr(self.data, 'modified', None)
        if modified is None:
            modified = time.time()
            self.data.modified = modified

        return modified

    @setproperty
    def modified(self, value):
        self.data.modified = value

    def add(self, comment):
        lastid = self.lastid

        name = '%0.3d'%lastid()
        lastid.change(1)

        self[name] = comment
        return self[name]

    def __len__(self):
        context = self.context
        length = len(self.data)

        if self.status == 4 and \
                            not checkPermission('zojax.ModifyContent', context):
            catalog = getCatalog()

            length = len(catalog.search(
                content=context,
                approved=(True,)))

        return length


@component.adapter(IComment, IObjectAddedEvent)
def commentAddedHandler(comment, ev):
    event.notify(CommentAddedEvent(comment.content, comment))


@component.adapter(IComment, IObjectRemovedEvent)
def commentRemovedHandler(comment, ev):
    extension = IContentDiscussion(comment.content)
    removeAllProxies(extension).modified = time.time()
    CommentsTag.update(extension.context)
    event.notify(CommentRemovedEvent(comment.content, comment))


@component.adapter(IComment, IObjectModifiedEvent)
def commentModifiedHandler(comment, ev):
    extension = IContentDiscussion(comment.content)
    removeAllProxies(extension).modified = time.time()
    CommentsTag.update(extension.context)


@component.adapter(IContentDiscussion, IContainerModifiedEvent)
def extensionModifiedEvent(extension, ev):
    removeAllProxies(extension).modified = time.time()
    CommentsTag.update(extension.context)


@component.adapter(IOpenDiscussible, IIntIdAddedEvent)
def discussibleContentCreated(object, event):
    IContentDiscussion(object).status = 1


@component.adapter(IDiscussible, IIntIdRemovedEvent)
def discussibleContentRemoved(object, event):
    extension = IContentDiscussion(object)

    for key in list(extension.keys()):
        del extension[key]


def getCommentsText(content):
    discussion = IContentDiscussion(content, None)
    if discussion is None:
        return u''

    return u'\n'.join([ob.comment for ob in discussion.values()])
