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
from zope.component import getUtility
from zope.app.security.interfaces import IAuthentication

from zojax.layoutform import Fields
from zojax.wizard.step import WizardStepForm
from zojax.wizard.interfaces import ISaveable

from zojax.content.discussion.interfaces import IComment, _

class CommentEditForm(WizardStepForm):
    interface.implements(ISaveable)

    name = 'content'
    title = _('Content')
    label = _('Modify content')

    @property
    def fields(self):
        fields = Fields(IComment)

        if not getattr(self.context, 'authorName'):
            fields = fields.omit('captcha', 'authorName')
        else:
            fields = fields.omit('captcha')

        return fields
