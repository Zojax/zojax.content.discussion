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
from zope.security import checkPermission
from zope.security.proxy import removeSecurityProxy
from zope.publisher.interfaces import NotFound
from zope.location import LocationProxy
from zope.traversing.browser import absoluteURL

from zojax.layoutform.form import PageletForm
from zojax.layoutform import button
from zojax.ownership.interfaces import IOwnership
from zojax.batching.batch import Batch

from zojax.wizard.interfaces import ISaveAction
from zojax.content.forms import wizardedit
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.discussion.interfaces import _, IContentDiscussion


class ManageDiscussion(object):

    label = _(u'Manage discussion')
    title = label
    size = 30

    def update(self):
        self.discussion = IContentDiscussion(self.context)
        self.batch = Batch(self.discussion.values(), size=self.size, request=self.request)
        super(ManageDiscussion, self).update()

    @button.buttonAndHandler(_(u'Back'), name='content.discussion.back')
    def handleBack(self, action):
        self.redirect('.')

    @button.buttonAndHandler(_(u'Remove'), name='content.discussion.remove')
    def handleRemove(self, action):
        request = self.request
        ids = request.get('commentIds', ())
        if not ids:
            IStatusMessage(request).add(_('Please select comments.'))

        else:
            for id in ids:
                if id in self.discussion:
                    del self.discussion[id]

            IStatusMessage(request).add(
                _('Selected comments have been removed.'))
            self.redirect(self.request.getURL())

    def canManage(self, comment):
        return checkPermission('zojax.ModifyContent', self.context) or \
        checkPermission('zojax.ModifyContent', comment)

    def publishTraverse(self, request, name):
        self.discussion = IContentDiscussion(self.context)
        if name in self.discussion:
            comment  = self.discussion[name]
            if self.canManage(comment):
                return LocationProxy(self.discussion[name], self, name)
        raise NotFound(self.context, name, request)


class EditContentWizard(wizardedit.EditContentWizard):
    handlers = wizardedit.EditContentWizard.handlers.copy()

    @button.handler(ISaveAction)
    def handleApply(self, action):
        wizardedit.EditContentWizard.handleApply(self, action)

        if not self.step.isComplete():
            return
        self.redirect("%s/" % absoluteURL(self.context.content, self.request))

    def isLastStep(self):
        return True

    def isFirstStep(self):
        return True
