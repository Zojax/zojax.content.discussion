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
from zope import component
from zope.app.intid.interfaces import IIntIdAddedEvent, IIntIdRemovedEvent

from zojax.topcontributors.api import contribute

from interfaces import IComment

COMMENTADDED = 1
COMMENTREMOVED = -2


@component.adapter(IComment, IIntIdAddedEvent)
def commentAddedHandler(comment, event):
    contribute(comment.content, comment.author, COMMENTADDED)


@component.adapter(IComment, IIntIdRemovedEvent)
def commentRemovedHandler(comment, event):
    content = comment.content

    # if manager manage comments
    if content.__parent__ is not None:
        contribute(comment.content, comment.author, COMMENTREMOVED)
