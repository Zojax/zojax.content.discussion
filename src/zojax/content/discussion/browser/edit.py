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
from zope import interface
from zojax.layoutform import button, Fields, PageletEditSubForm
from zojax.content.type.interfaces import IDraftedContent
from zojax.content.discussion.interfaces import IContentDiscussion


class ContentDiscussonEdit(PageletEditSubForm):

    prefix = 'content.discussion'

    @property
    def fields(self):
        return Fields(self.extension.__schema__)

    def getContent(self):
        return self.extension

    def update(self):
        self.drafted = IDraftedContent.providedBy(self.context)
        self.extension = IContentDiscussion(self.context, None)

        super(ContentDiscussonEdit, self).update()

    def isAvailable(self):
        return self.extension is not None
