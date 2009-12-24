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

    def listComments(self):
        context = self.discussion
        for idx in context:
            yield context[idx]

    def update(self):
        request = self.request
        if 'content.discussion.back' in request:
            self.redirect('.')
            return

        self.discussion = IContentDiscussion(self.context.context)

        if 'content.discussion.remove' in request:
            ids = request.get('commentIds', ())
            if not ids:
                IStatusMessage(request).add(_('Please select comments.'))

            else:
                for id in ids:
                    if id in self.discussion:
                        del self.discussion[id]

                IStatusMessage(request).add(
                    _('Selected comments have been removed.'))
