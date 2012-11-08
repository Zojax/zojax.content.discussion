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
import logging

from zope import interface, component
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zojax.content.discussion.interfaces import IContentDiscussionAware
from zojax.content.discussion.cache import CommentsTag

from  interfaces import IContentDiscussionConfig, \
                 IContentDiscussionConfiglet

logger = logging.getLogger('zojax.content.discussion (configlet)')

class ContentDiscussionConfiglet(object):
    pass


@component.adapter(IContentDiscussionAware)
@interface.implementer(IContentDiscussionConfig)
def getConfig(context):
    return component.getUtility(IContentDiscussionConfiglet)


@component.adapter(IContentDiscussionConfiglet, IObjectModifiedEvent)
def configletModified(ob, event):
    CommentsTag.update(ob)
