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
from zojax.content.discussion.interfaces import IComment
"""

$Id$
"""
from zope import interface, component
from persistent import Persistent
from zope.location import Location
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser import absoluteURL
from zope.app.container.interfaces import IObjectRemovedEvent

from zojax.catalog.utils import getRequest
from zojax.ownership.interfaces import IOwnership
from zojax.security.utils import getPrincipal

from interfaces import ISimpleComment, IThreadedComment, IContentDiscussion

from utils import getAthorFromCookie


class Comment(Persistent, Location):
    interface.implements(ISimpleComment, IThreadedComment)

    date = None
    anonymous = False
    title = u''
    parent = None
    children = None

    authorName = FieldProperty(ISimpleComment['authorName'])
    approved = FieldProperty(ISimpleComment['approved'])

    def __init__(self, author, comment):
        self.comment = comment
        self.author = author

    @property
    def content(self):
        return self.__parent__.__parent__

    @property
    def id(self):
        return self.__name__

    @property
    def url(self):
        url="%s/@@managediscussion/%s/context.html"
        return url % (absoluteURL(self.content, getRequest()), self.id)

    def addChild(self, comment):
        children = self.children
        if children is None:
            children = []

        children.append(removeAllProxies(comment))
        self.children = children

    def removeChild(self, comment):
        children = self.children
        if children is None:
            return

        comment = removeAllProxies(comment)
        if comment in children:
            children.remove(comment)

        self.children = children

    def setParent(self, comment):
        if self.parent is not None:
            self.parent.removeChild(self)

        self.parent = removeAllProxies(comment)
        if self.parent is not None:
            comment.addChild(self)

    def unsetParent(self):
        parent = self.parent
        if parent is not None:
            parent.removeChild(self)

        if self.children:
            for child in self.children:
                child.setParent(parent)

    def isAvailable(self):
        """ visible with the approval
        """
        content = self.content

        if IContentDiscussion(content).status == 4:
            if not checkPermission('zojax.ModifyContent', content):

                cookieAuthor = getAthorFromCookie(getRequest())
                print '============================================'
                print 'author name:', self.authorName
                print 'author from cookie:', getAthorFromCookie(getRequest())
                print 'check:', cookieAuthor == self.authorName
                print 'comment:', self.comment
                print '============================================'
                if cookieAuthor == self.authorName:
                    return True
                return self.approved

        return True


class CommentOwnership(object):

    component.adapts(IComment)
    interface.implements(IOwnership)

    def __init__(self, context):
        self.context = context
        self.ownerId = context.author
        self.owner = getPrincipal(context.author)
        self.isGroup = False


@component.adapter(ISimpleComment, IObjectRemovedEvent)
def commentRemovedHandler(comment, event):
    removeAllProxies(comment.unsetParent())
