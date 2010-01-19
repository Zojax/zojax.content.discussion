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
from zope.proxy import removeAllProxies
from zope.app.component.interfaces import ISite
from zope.traversing.browser import absoluteURL

from zojax.content.browser.interfaces import _
from zojax.statusmessage.interfaces import IStatusMessage


class DeleteContent(object):

    def update(self):
        if 'form.delete.content' in self.request:
            url = absoluteURL(self.context.content, self.request)
            if checkPermission('zojax.DeleteContent', self.context):
                del removeAllProxies(self.context).__parent__[self.context.__name__]

            IStatusMessage(self.request).add(_('Comment has been deleted.'))
            self.redirect(url)
            return

        elif 'form.delete.cancel' in self.request:
            self.redirect('./')
            return

        super(DeleteContent, self).update()
